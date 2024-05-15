import json
import logging
import os
from typing import Tuple

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

# Create an OpenAI client
client = OpenAI(api_key=api_key)


def create_batch_job(requests_file: str, batch_description: str, completion_window="24h") -> str:
    """
    Create a batch job to generate completions for the requests.

    :param requests_file: Path to the file containing the requests.
    :param batch_description: Description of the batch job.
    :param completion_window: The time window for the completion.
    :return: Path to the file containing the batch job details.
    """
    try:
        # Upload the file for the batch API
        with open(requests_file, "rb") as file:
            batch_input_file = client.files.create(
                file=file,
                purpose="batch"
            )
        batch_input_file_id = batch_input_file.id

        # Create a new batch job
        batch_work = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window=completion_window,
            metadata={
                "description": batch_description,
            }
        )

        # Save the batch_work to a JSON file
        batch_id = batch_work.id
        batch_work_path = f"batch_work_{batch_id}.json"
        with open(batch_work_path, "w") as file:
            json.dump(batch_work.to_dict(), file, indent=4)

        logger.info(f"Batch job created successfully: {batch_work_path}")
        return batch_work_path

    except FileNotFoundError:
        logger.error(f"The file {requests_file} does not exist.")
        raise
    except OpenAIError as e:
        logger.error(f"An error occurred while creating the batch job: {e}")
        raise RuntimeError(f"An error occurred while creating the batch job: {e}")


def check_status(batch_work_file: str) -> Tuple[str, dict]:
    """
    Check the status of the batch job.

    :param batch_work_file: Path to the file containing the batch job details.
    :return: Status of the batch job: 'completed', 'running', or 'failed'.
    """
    try:
        with open(batch_work_file, 'r') as json_file:
            data = json.load(json_file)
            batch_id = data['id']
            batch_info = client.batches.retrieve(batch_id)
            return batch_info.status, batch_info.to_dict()

    except FileNotFoundError:
        logger.error(f"The file {batch_work_file} does not exist.")
        raise
    except json.JSONDecodeError:
        logger.error(f"The file {batch_work_file} is not a valid JSON file.")
        raise ValueError(f"The file {batch_work_file} is not a valid JSON file.")
    except OpenAIError as e:
        logger.error(f"An error occurred while checking the batch job status: {e}")
        raise RuntimeError(f"An error occurred while checking the batch job status: {e}")


def extract_results(batch_work_file: str, output_file: str) -> None:
    """
    Extract the results from the batch job and save them to a file.

    :param batch_work_file: Path to the file containing the batch job details.
    :param output_file: Path to the file to save the results.
    """
    try:
        status, batch_info = check_status(batch_work_file)
        if status != 'completed':
            logger.error(f"The batch job is not completed yet. Current status: {status}")
            raise RuntimeError(f"The batch job is not completed yet. Current status: {status}")

        output_file_id = batch_info['output_file_id']
        # Update the bactch_worf_file with the output_file_id
        with open(batch_work_file, "w") as file:
            json.dump(batch_info, file, indent=4)

        content = client.files.content(output_file_id).content.decode('utf-8')
        with open(output_file, 'w') as file:
            file.write(content)

        logger.info(f"Results extracted successfully to {output_file}")

    except FileNotFoundError:
        logger.error(f"The file {batch_work_file} does not exist.")
        raise
    except json.JSONDecodeError:
        logger.error(f"The file {batch_work_file} is not a valid JSON file.")
        raise ValueError(f"The file {batch_work_file} is not a valid JSON file.")
    except OpenAIError as e:
        logger.error(f"An error occurred while extracting the results: {e}")
        raise RuntimeError(f"An error occurred while extracting the results: {e}")
