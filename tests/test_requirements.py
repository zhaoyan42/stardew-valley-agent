import os

def test_requirements_exists():
    print("Checking if environment/requirements.txt exists...")
    assert os.path.exists("environment/requirements.txt"), "environment/requirements.txt does not exist"

def test_requirements_content():
    print("Checking content of environment/requirements.txt...")
    required = ["mcp", "langchain", "mem0ai", "chromadb", "openai", "anthropic", "python-dotenv"]
    with open("environment/requirements.txt", "r") as f:
        content = f.read()
    for pkg in required:
        assert pkg in content, f"Package {pkg} not found in requirements.txt"

if __name__ == "__main__":
    try:
        test_requirements_exists()
        test_requirements_content()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
