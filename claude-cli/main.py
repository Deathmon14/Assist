#!/usr/bin/env python3
from rich.console import Console
from rich.prompt import Prompt
from agent.actions import handle_command
import sys

console = Console()

def show_help():
    console.print("[bold]Claude CLI Commands:[/bold]")
    console.print("  [cyan]search[/cyan] <pattern>  - Find code patterns")
    console.print("  [cyan]explain[/cyan] <file>    - Explain a code file")
    console.print("  [cyan]run[/cyan] <command>     - Execute shell command")
    console.print("  [cyan]edit[/cyan] <file>       - Modify a file with AI")
    console.print("  [cyan]test[/cyan] <path>       - Generate tests")
    console.print("  [cyan]exit[/cyan]             - Quit")

def main():
    console.print("[bold green]🤖 Claude CLI (Gemma 12B)[/]", justify="center")
    show_help()
    
    while True:
        try:
            text = Prompt.ask("\n[bold]>>[/bold] ")
            if text.lower() in ("exit", "quit"): break
            if text == "help": show_help()
            
            response = handle_command(text)
            console.print(f"[blue]{response}[/blue]")
            
        except KeyboardInterrupt:
            continue
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()