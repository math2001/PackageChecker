# PackageChecker

Due to the amount of pull requests on the [package_control_channel](https://github.com/wbond/package_control_channel), @FichteFoll had the idea to created [some automated tests](https://github.com/packagecontrol/package_reviewer).

They're good, the only problem is that it's not compatible with Sublime Text Python's version.

## Dependencies

Because PackageChecker clones your repo to check them, it needs `git` available in the command line. 

### Contributing

If you want to create a new `Checker`, have a look in here: [`checkers`](checkers/)
