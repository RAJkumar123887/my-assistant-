"""Chat with your assistant in the terminal. Great for testing the brain first."""
import brain


def main() -> None:
    print(f"Assistant ready (model: {brain.MODEL}). Type 'exit' to quit, 'reset' to forget.")
    while True:
        text = input("You: ").strip()
        if not text:
            continue
        if text.lower() in {"exit", "quit"}:
            break
        if text.lower() == "reset":
            brain.reset("terminal")
            print("AI: Memory cleared.")
            continue
        print("AI:", brain.reply("terminal", text))


if __name__ == "__main__":
    main()
