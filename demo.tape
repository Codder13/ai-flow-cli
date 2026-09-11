Output demo.gif
Output demo.mp4

Set FontSize 14
Set FontFamily "CaskaydiaMono Nerd Font"
Set LineHeight 1.25
Set Width 1240
Set Height 760
Set Padding 20
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set BorderRadius 8
Set TypingSpeed 30ms

# Reset session cleanly before starting
Hide
Type "export NO_COLOR="
Enter
Type "ai --clear"
Enter
Type "clear"
Enter
Show

Sleep 500ms

# 1. Natural unquoted question with syntax highlighted code blocks
Type "ai how do I find files larger than 100MB in current dir?"
Sleep 400ms
Enter
Sleep 8s

# 2. Seamless tab session continuity without quotes
Type "ai now sort them by size"
Sleep 400ms
Enter
Sleep 9s

# 3. Unix pipeline processing via stdin
Type "echo 'def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)' | ai make this iterative in python"
Sleep 500ms
Enter
Sleep 8s

Sleep 2s
