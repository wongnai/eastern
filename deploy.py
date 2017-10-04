#!/usr/bin/env python2.7
import sys
import os
import subprocess
import fileformatter
import time
import traceback
import urllib2

EXISTING_COMMAND = ["project", "job", "generate"]

CMD_GET_JOB_POD_NAME = "kubectl -n {} get pod --selector=job-name={} --output=jsonpath={{.items..metadata.name}}"
CMD_POD_PHASE = "kubectl -n {} get pod {} -o jsonpath={{.status.phase}}"
CMD_POD_RAW = "kubectl -n {} get pod {} -o yaml"
CMD_POD_OUTPUT = "kubectl -n {} logs {}"
CMD_DELETE_JOB = "kubectl -n {} delete job {}"
CMD_KUBE_CREATE = "kubectl -n {} create -f {}"
CMD_KUBE_APPLY = "kubectl -n {} apply -f {}"

def write_file(file_path, data):
    '''
    write data to file
    '''
    filep = open(file_path, "w+")
    filep.write(data)
    filep.close()

def run_shell(cmd, debug=False):
    '''
    invoke shell command and return output as result, raise exception if non-zero exit
    '''
    if debug:
        print "Run command: " + cmd
    return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

def run_shell_ignore(cmd, debug=False):
    try:
        print run_shell(cmd, debug)
    except subprocess.CalledProcessError as err:
        print err.output

_is_gke = None
def is_gke():
    '''Detect whether we're running in GKE'''
    global _is_gke
    if _is_gke is not None:
        return _is_gke

    # both aws and goog have this ip
    try:
        metadata = urllib2.urlopen('http://169.254.169.254/', timeout=1)
        metadata_header = metadata.info()
        _is_gke = 'metadata-flavor' in metadata_header and metadata_header['metadata-flavor'] == 'Google'
        print('is_gke: We\'re in GCP' if _is_gke else 'is_gke: We are in AWS-like')
        return _is_gke
    except urllib2.URLError:
        print('is_gke: Cannot connect to metadata service, assuming not cloud')
        _is_gke = False
        return _is_gke

def create_kube_ns(ns):
    create_call = subprocess.Popen(
        "kubectl create namespace " + ns,
        shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE
    )
    create_call.communicate()
    if 'AlreadyExists' in create_call.stdout.read():
        return

    # At this point a new namespace was created, deploy namespace fixtures
    if is_gke():
        run_shell(os.path.join(os.path.dirname(__file__), 'scripts', 'namespace-fixture.sh')+ ' ' + ns)

def run_kube(file_path, env, temp_kube_config_file_path, use_create=False):
    '''
    run kube with given file path
    '''
    kube_config_file = fileformatter.format(file_path, env)
    print kube_config_file

    # write into temp
    if not os.path.exists("temp"):
        os.makedirs("temp")

    print temp_kube_config_file_path
    write_file(temp_kube_config_file_path, kube_config_file)

    namespace = env['NAMESPACE']

    # create kube namespace
    create_kube_ns(namespace)

    try:
        # apply file to kube
        print "applying kube config"
        cmd = CMD_KUBE_CREATE if use_create else CMD_KUBE_APPLY
        result = run_shell(cmd.format(namespace, temp_kube_config_file_path))
        print result
    except:
        print "Error while running kube file=" + temp_kube_config_file_path
        raise
    finally:
        # remove temp file
        os.remove(temp_kube_config_file_path)

def deploy(project, namespace, image_tag):
    '''
    run deploy kubernetes.yaml
    '''
    # format file
    env = {
        "NAMESPACE": namespace,
        "IMAGE_TAG": image_tag
    }
    file_path = os.sep.join(["projects", project, "kubernetes.yaml"])

    temp_file_name = "{}_{}_{}.yaml".format(project, namespace, str(int(time.time())))
    temp_kube_config_file_path = os.sep.join(["temp", temp_file_name])

    run_kube(file_path, env, temp_kube_config_file_path)

def generate(project, namespace, image_tag):
    '''
    generate kubernetes.yaml deployment
    '''
    # format file
    env = {
        "NAMESPACE": namespace,
        "IMAGE_TAG": image_tag
    }
    file_path = os.sep.join(["projects", project, "kubernetes.yaml"])

    kube_config_file = fileformatter.format(file_path, env)
    print kube_config_file

def safe_print_pod_log_or_status(pod_name, namespace):
    if not pod_name:
        return

    try:
        print run_shell(CMD_POD_OUTPUT.format(namespace, pod_name))
    except subprocess.CalledProcessError:
        try:
            print "Cannot get log from pod_name=" + pod_name + ", will get raw pod instead"
            print run_shell(CMD_POD_RAW.format(namespace, pod_name))
        except subprocess.CalledProcessError:
            pass

def safe_delete_job(job_name, namespace):
    try:
        print "cleaning up job: " + job_name
        run_shell(CMD_DELETE_JOB.format(namespace, job_name))
    except Exception as e:
        print("Failed to cleanup job: '" + job_name + "'." +
                "You should run `kubectl -n " + namespace + " delete job " + job_name + "` manually.")
        print e

def job(file_path, job_name, namespace, image_tag):
    '''
    run kube job
    '''
    # format file
    env = {
        "NAMESPACE": namespace,
        "IMAGE_TAG": image_tag,
        "JOB_NAME": job_name
    }
    if not os.path.isabs(file_path):
        file_path = os.sep.join(["projects", file_path])
    temp_file_name = "{}_{}_{}.yaml".format(job_name, namespace, str(int(time.time())))
    temp_kube_config_file_path = os.sep.join(["temp", temp_file_name])

    try:
        pod_name = False

        run_kube(file_path, env, temp_kube_config_file_path)
        pod_name = run_shell(CMD_GET_JOB_POD_NAME.format(namespace, job_name))
        if not pod_name:
            raise Exception("Cannot find pod form job name: {}. Please ensure job is not exist.".format(job_name))

        print "running job: " + job_name + " pod_name: " + pod_name

        phase = run_shell(CMD_POD_PHASE.format(namespace, pod_name))
        for _ in range(1, 100):
            if phase != "Pending":
                break
            time.sleep(1)
            phase = run_shell(CMD_POD_PHASE.format(namespace, pod_name))

        while True:
            time.sleep(1)
            phase = run_shell(CMD_POD_PHASE.format(namespace, pod_name))
            if phase == "":
                break
            if phase == "Succeeded":
                break
            if phase == "Running":
                continue

            print "Phase type:" + str(type(phase)) + " => `" + str(phase) + "`"
            raise Exception("Running job failed with status: " + phase)
    finally:
        if "pod_name" in locals():
            safe_print_pod_log_or_status(pod_name, namespace)
        safe_delete_job(job_name, namespace)

if __name__ == "__main__":
    if len(sys.argv) < 5 or sys.argv[1] not in EXISTING_COMMAND:
        print """Invalid parameters provided
        Usage:
            ./deploy.py generate [project-name] [namespace] [image-tag]
            ./deploy.py project [project-name] [namespace] [image-tag]
            ./deploy.py job [job-file-path] [job-name] [namespace] [image-tag]
        """
        exit(1)

    try:
        if sys.argv[1] == "generate":
            generate(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == "project":
            deploy(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == "job":
            job(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        else:
            print """Deploy error: invalid command {}""".format(sys.argv[1])
            raise Exception("invalid command")
    except subprocess.CalledProcessError as err:
        print err
        print err.output
        traceback.print_exc()
        exit(err.returncode)
