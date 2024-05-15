# OpenAI Batch Processing Project

This project is a Python application that uses the OpenAI API to create batch
jobs, check their status, and extract the results.

Check
the [OpenAI API documentation](https://platform.openai.com/docs/guides/batch).

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes.

### Prerequisites

Check the `requirements.txt` file for the required packages.

### Installing

Clone the repository to your local machine:

```bash
git clone https://github.com/Dntfreitas/batch-api-openai
```

Navigate to the project directory:

```bash
cd batch-api-openai
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project directory with the following content:

```bash
OPENAI_API_KEY=your_openai_api_key
```

### Usage

The project contains several functions for interacting with the OpenAI API:

- `create_batch_job(requests_file: str, batch_description: str,
  completion_window="24h") -> str`: Creates a batch job with the requests in
  the file and returns the file name of the batch job.
- `check_status(batch_work_file: str) -> Tuple[str, dict]`: Checks the status of
  the batch job.
- `extract_results(batch_work_file: str, output_file: str) -> None`: Extracts
  the results from the batch job and saves them to a file.

### Example

The file `requests_example.jsonl` is an example of a file containing requests.

```python
from functions import create_batch_job, check_status, extract_results

# Create a batch job
file_batch = create_batch_job(requests_file="requests_example.jsonl",
                              batch_description="Batch job to generate completions")

# Check the status of the batch job
status, response = check_status(file_batch)
print(status)

# Extract the results from the batch job
extract_results(file_batch, "output.jsonl")
```