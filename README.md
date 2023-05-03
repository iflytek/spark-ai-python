# Iflytek SPark AI Python Library

The SparkAI Python library provides convenient access to the Iflytek SparkAI API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the SparkAI API.


## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package, just run:

```sh
pip install --upgrade spark_ai_sdk
```

Install from source with:

```sh
python setup.py install
```

### Optional dependencies

```
pip install spark_ai_sdk

````

## Usage



### Command-line interface


## Example code

todo

### Chat

Conversational models such as `gpt-3.5-turbo` can be called using the chat completions endpoint.

```python
import sparkai
openai.api_key = "sk-..."  # supply your API key however you choose

completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world!"}])
print(completion.choices[0].message.content)
```

## Credit

This library is forked from the [Stripe Python Library](https://github.com/stripe/stripe-python).
