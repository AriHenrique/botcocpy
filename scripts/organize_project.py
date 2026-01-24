"""
Script para organizar o projeto movendo arquivos para diretórios apropriados.
"""
import shutil
import os
from pathlib import Path

def organize_project():
    """Organiza o projeto movendo arquivos para diretórios apropriados."""
    project_root = Path(__file__).parent.parent
    
    print("=== Organizando projeto ===\n")
    
    # Criar diretórios se não existirem
    docs_dir = project_root / "docs"
    build_dir = project_root / "build"
    scripts_dir = project_root / "scripts"
    
    docs_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)
    
    # Mover documentação (exceto README.md principal)
    docs_files = [
        "ARCHITECTURE.md",
        "REFACTORING_SUMMARY.md",
        "README_BUILD.md",
        "BUILD_INSTRUCTIONS.md",
        "EXE_PREPARATION.md",
        "README_EXE.md",
        "INSTALL_MAKE.md",
        "MIGRATION_GUIDE.md",
    ]
    
    print("Movendo documentação...")
    for doc in docs_files:
        src = project_root / doc
        if src.exists():
            dst = docs_dir / doc
            shutil.move(str(src), str(dst))
            print(f"  [OK] {doc} -> docs/")
    
    # Mover arquivos de build
    build_files = [
        "build_exe.spec",
        "build_exe_debug.spec",
        "Makefile",
        "Makefile.ps1",
        "make.bat",
        "install_make.bat",
    ]
    
    print("\nMovendo arquivos de build...")
    for build_file in build_files:
        src = project_root / build_file
        if src.exists():
            dst = build_dir / build_file
            shutil.move(str(src), str(dst))
            print(f"  [OK] {build_file} -> build/")
    
    # Mover install.ps1 para scripts
    install_ps1 = project_root / "install.ps1"
    if install_ps1.exists():
        dst = scripts_dir / "install.ps1"
        shutil.move(str(install_ps1), str(dst))
        print(f"  [OK] install.ps1 -> scripts/")
    
    # Mover scripts Python utilitários para scripts/
    utility_scripts = [
        "grab_template.py",
        "normalize_troop_names.py",
        "minitouch_client.py",
    ]
    
    print("\nMovendo scripts utilitarios...")
    for script in utility_scripts:
        src = project_root / script
        if src.exists():
            dst = scripts_dir / script
            shutil.move(str(src), str(dst))
            print(f"  [OK] {script} -> scripts/")
    
    # Remover diretório resources duplicado (se vazio)
    resources_dup = project_root / "resources"
    if resources_dup.exists() and resources_dup.is_dir():
        try:
            if not any(resources_dup.iterdir()):
                resources_dup.rmdir()
                print(f"  [OK] Removido diretorio resources/ vazio")
        except:
            pass
    
    # Remover arquivos temporários
    temp_files = [
        "swipe_script.txt",
        "zoom_script.txt",
        "screen.png",
        "ui.xml",
    ]
    
    print("\nRemovendo arquivos temporários...")
    for temp_file in temp_files:
        src = project_root / temp_file
        if src.exists():
            try:
                src.unlink()
                print(f"  [OK] Removido {temp_file}")
            except Exception as e:
                print(f"  [WARN] Nao foi possivel remover {temp_file}: {e}")
    
    # Atualizar caminhos nos arquivos .spec
    print("\nAtualizando arquivos .spec...")
    for spec_file in ["build_exe.spec", "build_exe_debug.spec"]:
        spec_path = build_dir / spec_file
        if spec_path.exists():
            content = spec_path.read_text(encoding='utf-8')
            # Atualizar project_root para apontar para o root
            if 'project_root = Path(__file__).parent' in content:
                content = content.replace(
                    'project_root = Path(__file__).parent',
                    'project_root = Path(__file__).parent.parent  # build/ -> root'
                )
                spec_path.write_text(content, encoding='utf-8')
                print(f"  [OK] Atualizado {spec_file}")
    
    # Atualizar Makefile.ps1
    makefile_ps1 = build_dir / "Makefile.ps1"
    if makefile_ps1.exists():
        content = makefile_ps1.read_text(encoding='utf-8')
        # Atualizar caminhos
        if '$SpecFile = "build_exe.spec"' in content:
            content = content.replace(
                '$SpecFile = "build_exe.spec"',
                '$SpecFile = "build\build_exe.spec"'
            )
        if 'Join-Path $PSScriptRoot "scripts\\install_make.ps1"' in content:
            content = content.replace(
                'Join-Path $PSScriptRoot "scripts\\install_make.ps1"',
                'if (Test-Path "scripts\\install_make.ps1") { "scripts\\install_make.ps1" } else { "..\\scripts\\install_make.ps1" }'
            )
        makefile_ps1.write_text(content, encoding='utf-8')
        print(f"  [OK] Atualizado Makefile.ps1")
    
    print("\n=== Organização concluída! ===")
    print(f"\nEstrutura:")
    print(f"  docs/     - Documentação")
    print(f"  build/    - Arquivos de build")
    print(f"  scripts/  - Scripts utilitários")
    print(f"\nArquivos mantidos no root:")
    print(f"  README.md, main.py, main_new.py, gui.py")
    print(f"  pyproject.toml, poetry.lock")
    print(f"  PROJECT_STRUCTURE.md (novo)")

if __name__ == "__main__":
    organize_project()
