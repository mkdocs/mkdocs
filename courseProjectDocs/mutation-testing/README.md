# 🧬 Mutation Testing

**Target Modules:** `mkdocs/utils/__init__.py`, `mkdocs/utils/contrib/search/search_index.py`  
**Test Files:** `courseProjectCode/mutation-testing/test_utils_mutations.py` , `courseProjectCode/mutation-testing/test_utils_mutations.py`,`courseProjectCode/mutation-testing/test_content_section_eq.py`
**Configuration:** Defined in `pyproject.toml` under [tool.mutmut]  

## Workflow
It is recommended to run mutmut using hatch. This ensures that the correct virtual environment with all dependencies is used. Note that mutmut will not install if you do not have rust installed as well. Refer to the mutmut documentation if there are any issues installing. If you are using Windows, it is recommended to use WSL (Windows Subsystem for Linux) as mutmut requires Unix fork support. You can follow the steps [below](#workflow-windows-wsl) before running mutmut.
The command to run mutmut via hatch is:

```bash
hatch run mutmut:run
```

## 🔧 Workflow (Windows WSL)

1.  **Set WSL default to Ubuntu**

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

    This opens an interactive TUI (text user interface) where you can see each mutation. The sad faces were how I decided get_relative_url() was a good target. I added `mkdocs-AJ_Connor_Kemoy\tests\test_utils_mutations.py` and then ran mutmut again to analyse killed mutants.

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
