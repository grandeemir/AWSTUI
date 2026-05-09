import os
from dotenv import load_dotenv
from awstui.app import AWSTUIApp

def main():
    load_dotenv()
    app = AWSTUIApp()
    app.run()

if __name__ == "__main__":
    main()
