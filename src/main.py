import logging

# configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
     handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler('app.log', mode='w'),  # Log to a file (overwrite each run)
    ],
)

def main():
    pass

if __name__ == "__main__":
    main()