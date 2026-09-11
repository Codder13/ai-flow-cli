Output demo.gif
Output demo.mp4

Set FontSize 15
Set FontFamily "CaskaydiaMono Nerd Font"
Set LineHeight 1.3
Set Width 920
Set Height 520
Set Padding 18
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set BorderRadius 8
Set TypingSpeed 40ms

# Reset session cleanly before starting
Hide
Type "ai --clear"
Enter
Type "clear"
Enter
Show

Sleep 600ms

# 1. Quick Question with rich terminal output
Type "ai 'how do I find files larger than 100MB in current dir?'"
Sleep 300ms
Enter
Sleep 6s

# 2. Same-session follow-up continuity
Type "ai 'now sort them by size'"
Sleep 300ms
Enter
Sleep 6s

# 3. Unix Pipeline integration
Type "echo 'def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)' | ai 'make this iterative python'"
Sleep 400ms
Enter
Sleep 6s

Sleep 2s
