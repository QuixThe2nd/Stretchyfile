# Stretchyfile

Stretchyfile is a stretchy Caddyfile flavour. It is designed to simplify complex use-cases, by extending how variables and conditions function in Caddyfile.

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
${domain}:{ports} {
    if (host beta.example.com) {
        respond "Hello, world!"
    } else {
        respond "Goodbye, world!"
    }
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
example.com:80, example.com:443 {
    @condition0 {
        host beta.example.com
    }
    handle @condition0 {
        respond "Hello, world!"
    }
    @condition1 {
        not {
            host beta.example.com
        }
    }
    handle @condition1 {
        respond "Goodbye, world!"
    }
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
$ports = 80,443

${domains}:{ports} {
    respond "Hello, world!"
}
```

Simple, right?

Here's another way you can do it:

```
$domains = example.com,example.org
$ports = 80,443

${domains}:{ports}, *.{domains}:{ports} {
    respond "Hello, world!"
}
```

And another way:

```
$tlds = .com,.org
$ports = 80,443

$example{tlds}:{ports}, *.example{tlds}:{ports} {
    respond "Hello, world!"
}
```

And another (yes, you can concat arrays):

```
$domains = example.com,example.org
$domains = {domains},*.{domains}
$ports = 80,443

${domains}:{ports} {
    respond "Hello, world!"
}
```

### If / Else Statements
Caddyfile's if statements are great, but they can be a bit of a pain to use. Stretchyfile makes them a bit easier to use. Conditions are identical to Caddyfile's conditions. Though defining the if statement is a bit different. Stretchyfile uses a more uniform approach to if/else statements, matching the syntax of most programming languages.

Let's say you have example.com, and you want to route beta.example.com to a different server block. Here's how you would do it in Caddyfile:

```
*.example.com {
    @beta {
        host beta.example.com
    }
    handle @beta {
        respond "Hello, world!"
    }
    @not_beta {
        not {
            host beta.example.com
        }
    }
    handle @not_beta {
        respond "Hello, world!"
    }
}

```

The syntax is a bit difficult to remember, and it's a bit of a pain to write. Here's how you would do it in Stretchyfile:
```
*.example.com {
    if (host beta.example.com) {
        respond "Hello, world!"
    } else {
        respond "Hello, world!"
    }
}
```

A lot simpler, right? You can also use variables in your conditions:

```
$ports = 80, 443
$*.example.com:{ports} {
    if (host beta.example.com) {
        respond "Hello, world!"
    } else {
        respond "Hello, world!"
    }
}
```

Have multiple conditions? Easy, just use `&&` like any other programming language:

```
*.example.com {
    if (host beta.example.com && cookie beta) {
        respond "Hello, world!"
    } else {
        respond "Hello, world!"
    }
}
```

Here is the Caddyfile equivalent:

```
*.example.com {
    @beta {
        host beta.example.com
        cookie beta
    }
    handle @beta {
        respond "Hello, world!"
    }
    @not_beta {
        not {
            host beta.example.com
            cookie beta
        }
    }
    handle @not_beta {
        respond "Hello, world!"
    }
}
```

## Usage

Using Stretchyfile is super simple. Clone this repo, or copy `stretchy.py` to your machine.

If stretchy.py is in your Caddy directory, simply run:

```
python3 stretchy.py
```

Otherwise, you can specify your path name:

```
python3 stretchy.py /etc/caddy/Stretchyfile
```

## Troubleshooting

I have extensively tested this for my use-cases, but it is impossible for me to have caught every edge case. If your Stretchyfile isn't being transpiled properly, you can add a `-V` argument to the end to see what the transpiler is doing step-by-step to hopefully troubleshoot your issue. You can also optionally set `-V comment` to insert logs as comments in the Caddyfile instead of printing.
