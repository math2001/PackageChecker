# Checkers

Each files, called `checkers`, have one specific tasks. Please be sure to improve an existing one
instead of creating a new one.

## Creating a new `checkers`

If you want to create a new `checker`, here are the conditions:

- create a python file, starting by `check_`, and followed by a *snake_case* name. For example: `check_keymap.py`.
- inside it, create a class with the same name as your file, but in *CamelCase* (and stating with an upper case letter). For example: `CheckKeymap`
- make sure this class inherits from either `Checker`, or `FileChecker` (the last one is in fact a child of `Checker`, scroll down to read it's specificity). You can import this class in your `checker` like this: `from . import Checker` (those classes are defined in `checkers/__init__.py`).
- add a `.run()` method. This method will be called without any arguments. It's this function that will have to run the test.

Done! Your `checker` is now ready to do some cool stuff!

## Fundamental method

By inheriting from `Checker` (or `FileChecker`), you inherit from different methods, and here are the two principals:

- `fail(caption, *descriptions)`
- `warn(caption, *descriptions)`

As you guessed, those method are here to, respectively, raise fails and warnings. They both take the same arguments, and they both work the same ways. So, everything I'm going to say in this part for one works for the other.

As you saw above, you can give as many args as you want to those methods. The first one is the caption, and the others are 1 line of the description.

None of those methods stops the execution of the test suits. The point is give has many feedback in one run. So, in one test, you can raise several *fails*. It doesn't mean you *can't* stop the execution of you entire checker (you can't go higher than that for now), but you should try to avoid it. For example, in a keymap, you found a key binding that doesn't have a `command` key (so nothing will be run), and in an other one, you've found a context which is, instead of a list, an object for example.

### About the caption

The convention is to make sure the `caption` always stays the same for the same type of fails/warnings. So, it'd be for example: `An unallowed key has been found`, and not `The key <key> is not allowed`. It's in the descriptions that you're going to give more information about this specific fail/warning. Why? so that we can group those errors, to get a better output.

Also, in your caption, *do not* specific the name of your `checker`. It'll be automatically rendered above.

### About the descriptions

Your description should be composed of less than 4 lines at the most, and short lines (try not to get over 120 chars), but still clear. :smile: This means that you have to make sure where about the error is, but you shouldn't explain *how* to solve the error. The [wiki]() is here for this.

### Other methods

To know what other method you have access to, for now, have a look at the code in `checkers/__init__.py`

### `FileChecker`

As I told above, `FileChecker` is inheriting of `Checker`. All it adds is that it modifies the `fails` and `warns` method to add one line at the end of the description:

`Found in ` and the value of the instance variable `current_file` (`self.current_file`). It's useful when your checking several file, so you're looping over them, and on each of them, you run your test (or if you're organized, you call a function :wink:). Well, just add `self.current_file = ` and the name of the file that is currently being checked. Have a look at `checkers/check_keymap.py` to see a real-life example.
