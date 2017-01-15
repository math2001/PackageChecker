# PackageChecker

Due to the amount of pull requests on the [package_control_channel](https://github.com/wbond/package_control_channel), @FichteFoll had the idea to created [some automated tests](https://github.com/packagecontrol/package_reviewer).

They're good, the only problem is that it's not compatible with Sublime Text Python's version.

## Dependencies

Because PackageChecker clones your repo to check them, it needs `git` available in the command line.

## Usage

If you have Sublime Text *3*, you don't need to have `python` installed on your system. You just have to run the command `package_checker`. (you should bind a shortcut to it). Otherwise, you'll python *3* installed.

All this command does is: show an input in which you can type all the arguments for the commands, in a *terminal-way*. The output will be shown in an output panel.

So, everything is the same, except that you don't have to prefix your text with `python PackageChecker.py`

Just run `--help` to get started

*more coming soon*

### Contributing

If you want to create a new `Checker`, have a look in here: [`checkers`](checkers/)
