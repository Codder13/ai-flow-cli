Output demo.gif
Output demo.mp4

Set FontSize 14
Set FontFamily "CaskaydiaMono Nerd Font"
Set LineHeight 1.25
Set Width 1240
Set Height 780
Set Padding 20
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set BorderRadius 8
Set TypingSpeed 28ms

# Setup clean environment
Hide
Type "export NO_COLOR="
Enter
Type "ai --clear"
Enter
Type "clear"
Enter
Show

Sleep 400ms

# --- 1. Everyday CLI Query (Unquoted, Rich Markdown) ---
Type "ai how to find files larger than 100MB in current dir?"
Sleep 300ms
Enter
Sleep 8s

# --- 2. Automatic Tab Session Continuity ---
Type "ai now sort them by size"
Sleep 300ms
Enter
Sleep 9s

# --- 3. Pipeline / Stdin Code Transformation ---
Type "clear"
Enter
Sleep 400ms
Type "echo 'def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)' | ai make this iterative in python"
Sleep 400ms
Enter
Sleep 8s

# --- 4. Git Pipeline: Generating commit message from diff ---
Type "clear"
Enter
Sleep 400ms
Type "git diff PKGBUILD | ai write a concise commit message"
Sleep 400ms
Enter
Sleep 8s

# --- 5. Harness Switcher on the Fly (-H omp / claude / pi) ---
Type "clear"
Enter
Sleep 400ms
Type "ai -H omp write a fast oneliner to find external IP"
Sleep 400ms
Enter
Sleep 8s

# --- 6. Raw Pipeline output (--raw into unix tools) ---
Type "clear"
Enter
Sleep 400ms
Type "ai --raw calculate 2 to the power of 16 | tr -d ' ' | rev"
Sleep 400ms
Enter
Sleep 6s

Sleep 2s
