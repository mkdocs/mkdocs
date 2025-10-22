# 🧬 Mutation Testing

## AJ - Mutation Testing Overview

**Target Module:** `mkdocs/utils/__init__.py`  
**Test File:** `tests/test_utils_mutations.py`  
**Configuration:** Defined in `pyproject.toml` under [tool.mutmut]  

### 🔧 Workflow (Windows WSL)

1.  **Update WSL and set default to Ubuntu**

    ```bash
    wsl --set-default Ubuntu
    ```

2.  **Install Python in WSL**

    ```bash
    wsl
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

3.  **Navigate to project** (WSL can access Windows files in /mnt/)

    ```bash
    cd /mnt/c/Users/ajbar/ajsoftworks/mkdocs-AJ_Connor_Kemoy
    ```

4.  **Create virtual environment**

    ```bash
    python3 -m venv mkdocVenv
    source mkdocVenv/bin/activate
    ```

5.  **Install project dependencies and mutmut**

    ```bash
    pip install -e .
    pip install mutmut
    ```

6.  **Run mutmut**

    ```bash
    mutmut run
    ```

7.  **Browse Mutations Interactively**

    ```bash
    mutmut browse
    ```

    > This opens an interactive TUI (text user interface) where you can see each mutation. The sad faces were how I decided get_relative_url() was a good target. I added `mkdocs-AJ_Connor_Kemoy\tests\test_utils_mutations.py` and then ran mutmut again.

    ![Mutmut Browser](/courseProjectDocs/images/mutation_testing/3-mutmut-browse.png)

---

### 🎯 Quick Reference

 Command | Purpose
---------|---------
 `mutmut run` | Run mutation testing
 `mutmut results` | Show summary
 `mutmut browse` | Interactive UI

---

### 🐛 Troubleshooting

#### "ModuleNotFoundError: No module named 'resource'" on Windows

- mutmut requires Unix fork support
- Use WSL (see instructions above)

---

### 📚 Additional Resources

- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [What is Mutation Testing?](https://en.wikipedia.org/wiki/Mutation_testing)
- [Mutation Testing Best Practices](https://medium.com/hackernoon/mutmut-a-python-mutation-testing-system-9b9639356c78)
