# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [4.4.0] - 2019-06-14
### Changed
- Fix job issue due to wrong flag usage.

## [4.3.0] - 2018-11-03
### Changed
- Job now exit with code 3 when job failure status is greater than zero.

## [4.2.1] - 2018-10-01
### Fixed
- Republished due to unclean build directory. Now using CI to cleanly submit

## [4.2.0] - 2018-09-24
### Changed
- Deploy now exit with code 3 when `kubectl rollout wait` exit with status code

## [4.1.2] - 2018-08-17
### Fixed
- Republished due to unclean build directory

## [4.1.1] - 2018-08-06
### Changed
- Updated dependencies
- Docker now use Python 3.7
- Updated Kubernetes client in Docker image to 1.11.1

## [4.1.0] - 2018-07-06
### Changed
- Job deployment will always removed after job success or failed
- Fix exception raised when deploy job but pod was not scheduled

## [4.0.0] - 2018-06-15
### Added
- Pluggable formatters

### Changed
- BREAKING: The `formatter` module is moved to `yaml_formatter`. `formatter` now offer an abstract base class and the previous `format` function
- BREAKING: Unmatched variable now cause warning (#4, @blead)

## [3.0.1] - 2018-04-17
### Changed
- Set PYTHONUNBUFFERED in Docker
- Default timeout is 300s

## [3.0.0] - 2018-04-10
### Changed
- BREAKING: Timed out jobs now exit with status code 2
- BREAKING: Job timeout now count only idle time.
  - The previous behavior resulting in failing deployments when rollout involve many pods. A workaround is to adjust timeout based on expected number of pod. This new behavior ensure that the default timeout should be relevant regardless of number of pods. It should still be adjusted if the pod takes longer to start.
  - The new timeout timer will reset when output of `kubectl rollout status` changed.
- Updated kubectl

## [2.1.0] - 2017-12-22
### Added
- deploy/job now have `--timeout` option, defaulting to 60s

## [2.0.0] - 2017-12-22
### Changed
- Initial open source release 🎉

[4.4.0]: https://github.com/seehait/eastern/compare/v4.3.0...HEAD
[4.4.0]: https://github.com/seehait/eastern/compare/v4.3.0...v4.4.0
[4.3.0]: https://github.com/seehait/eastern/compare/v4.2.1...v4.3.0
[4.2.1]: https://github.com/seehait/eastern/compare/v4.2.0...v4.2.1
[4.2.0]: https://github.com/seehait/eastern/compare/v4.1.2...v4.2.0
[4.1.2]: https://github.com/seehait/eastern/compare/v4.1.1...v4.1.2
[4.1.1]: https://github.com/seehait/eastern/compare/v4.1.0...v4.1.1
[4.1.0]: https://github.com/seehait/eastern/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/seehait/eastern/compare/v3.0.1...v4.0.0
[3.0.1]: https://github.com/seehait/eastern/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/seehait/eastern/compare/v2.1.0...v3.0.0
[3.0.0]: https://github.com/seehait/eastern/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/seehait/eastern/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/seehait/eastern/compare/ae1c40a3dbf1a639ffaf5bc0034268b239ac1e3e...v2.0.0
