# Stretchyfile
Stretchyfile is a stretchy Caddyfile flavour. It is designed to simplify complex use-cases, by extending how variables function in Caddyfile.

## Example

### Input Stretchyfile
```
$port = 80
$ports = 80,443
$domain = example.com
$domains = example.com,example.org

$:{port} {
    respond "Hello, world!"
}
$:{ports} {
    respond "Hello, world!"
}
${domain} {
    respond "Hello, world!"
}
${domains} {
    respond "Hello, world!"
}
${domain}:{port} {
    respond "Hello, world!"
}
${domain}:{ports} {
    respond "Hello, world!"
}
${domains}:{port} {
    respond "Hello, world!"
}
${domains}:{ports} {
    respond "Hello, world!"
}
```

### Output Caddyfile
```
:80 {
    respond "Hello, world!"
}
:80, :443 {
    respond "Hello, world!"
}
example.com {
    respond "Hello, world!"
}
example.com, example.org {
    respond "Hello, world!"
}
example.com:80 {
    respond "Hello, world!"
}
example.com:80, example.com:443 {
    respond "Hello, world!"
}
example.com:80, example.org:80 {
    respond "Hello, world!"
}
example.com:80, example.org:80, example.com:443, example.org:443 {
    respond "Hello, world!"
}
```

## Syntax

The syntax of Stretchyfile is very similar to Caddyfile's syntax. In fact, you can input a raw Caddyfile and it will output the exact same Caddyfile. Any line of code that uses Stretchyfile-specific code, must start with a `$`, otherwise it'll be skipped over.

### Variables

You can declare a variable at any point within your code. At the top, in the middle, wherever.

Here's how you set a variable:
```
$port = 80
```

To use a variable, you need to add a $ at the start of the line where you want to use the variable. You then insert the variable name wrapped with `{}`.

Here's a real-world example of how you would use a variable:
```
$port = 80

$example.com:{port} {
    respond "Hello, world!"
}
```

You are free to use variables for any value. The only exception is ports. It is crucial that if you want to save a port to a variable, you **do not** include a `:`. This is important for mapping array variables which are explained further down.
**Do not do this**:
```
$port = :80

$example.com{port} {
    respond "Hello, world!"
}
```

### Arrays
Array's are why I made Stretchyfile. For sites with a more complicated setup, arrays are a life-saver.

Here's an example of the problem I'm trying to solve:
```
example.com:80, example.com:443, *.example.com:80, *.example.com:443, example.org:80, example.org:443, *.example.org:80, *.example.org:443 {
    respond "Hello, world!"
}
```

And the worst part is, this is a common setup. If you have multiple domains, use multiple ports, or have many subdomains, I am sure your Caddyfile is a mess (like mine).

Here's how the above example looks with Stretchyfile:
```
$domains = example.com,example.org,*.example.com,*.example.org
$port = 80,443

${domains}:{ports} {
    respond "Hello, world!"
}
```

Simple, right?

Here's another way you can do it:
```
$domains = example.com,example.org
$port = 80,443

${domains}:{ports}, *.{domains}:{ports} {
    respond "Hello, world!"
}
```

And another way:
```
$tlds = .com,.org
$port = 80,443

$example{tlds}:{ports}, *.example{tlds}:{ports} {
    respond "Hello, world!"
}
```

And another:
```
$domains = example.com,example.org
$domains = {domains},*.{domains}
$port = 80,443

${domains}:{ports} {
    respond "Hello, world!"
}
```

## Usage
Using Stretchyfile is super simple. Clone this repo, or copy `strechy.py` to your machine.

If stretchy.py is in your Caddy directory, simply run:
```
python3 stretchy.py
```

Otherwise, you can specify your path name:
```
python3 stretchy.py /etc/caddy/Stretchyfile
```
