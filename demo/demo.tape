# vhs demo tape — https://github.com/charmbracelet/vhs
# Renders demo/demo.gif, which is a far better flex than any badge row.
# Replace the Type/Enter lines with a real command worth watching.

Output demo/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 620
Set Padding 24
Set Theme "Dracula"
Set TypingSpeed 45ms

Type "# a real terminal recording beats 20 static badges"
Enter
Sleep 800ms

Type "cargo run --release"
Enter
Sleep 4s

Sleep 1s
