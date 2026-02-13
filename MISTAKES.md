# Mistakes (Do Not Repeat)

- ❌ **Windows Bash tool is Git Bash (MSYS/MINGW64)**: Do NOT use `cd /d`, `dir`, or CMD backslash paths. Use Unix paths (`/d/dev/...`), `ls`, `mkdir -p`. For `mklink` use `cmd.exe /c "..."`. For `.ps1` scripts use `powershell.exe -ExecutionPolicy Bypass -File script.ps1`.
- ❌ **Git worktree cleanup order**: Remove the worktree BEFORE deleting the branch. `git branch -d` fails if the branch is still checked out in a worktree. Correct order: `git worktree remove <path>` then `git branch -d <branch>`.
