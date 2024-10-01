<h1 align="center">
    fuzz_lang &#128679;
</h1>

A basic implementation of a compiler for `fuzz-lang`.

`fuzz-lang` is compiled (transpiled) to rust.

## Prerequisites
* `rustc` - the rust compiler: [https://www.rust-lang.org/learn/get-started](https://www.rust-lang.org/learn/get-started)

## What the fuck is `fuzz-lang`
`fuzz-lang` is a toy language used to help me understand how the "front-end" of a compiler works.

I got carried away and thought I'd add some weird things in.

Here's some `fuzz-lang` comments detailing the main rules of the language.

```
comment: `fuzzy` is an assignment statement - fuzz-lang is statically typed so all
comment: variables and function must be annotated.

comment: `labs` is a print statement

comment: `suzy` declares a function - functions can only receive a single input

comment: all functions must end with `flabs`

comment: to denote the types you must annotate the function with curly brackets
comment: showing how the input type transitioned to the output type.

comment: to create an array use the `array` type declare the data type the array should
comment: contain and the number of values then declare the identifier for the array.
comment: e.g., fuzzy array[int; 5] collection = [0, 1, 2, 3, 4];

comment: to then loop through an array use the keywords `every` and `from`.
comment: e.g., every item from collection { labs(item); }
```

Here's an example program to create an array of values and then square each value in the array:

```
fuzzy array[int; 5] collection = [0, 1, 2, 3, 4];

every item from collection {
    fuzzy int item_squarred = item * item;
    labs(item_squarred);
}
```

## How do I compile `fuzz-lang`?

Clone this repository and then run the following:

```make fuzz-lang```

Then start compiling `fuzz` to executables:

```
fuzz-lang examples/hello_world.fuzz hello_world
```

Execute program:

```
./hello_world
```

# &#127939; How do I get started?
You don't.
