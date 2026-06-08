name: Run Quick Test
on: [workflow_dispatch]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # This step lists all files found by the runner
      - name: List all files in the directory
        run: ls -R
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      # This looks for the file wherever it might be
      - name: Find and run test
        run: |
          find . -name "quick_test.py" -exec python3 {} \;
