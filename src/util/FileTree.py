import fnmatch
import os


def load_gitignore_patterns(gitignore_path='../../.gitignore'):
    patterns = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.add(line)
    return patterns


IGNORED_EXTENSIONS = {
    '.log', '.tmp', '.pyc', '.lock', '.swp'
}

IGNORED_NAMES = {
    'node_modules', '__pycache__', '.git', '.DS_Store', 'FileTree.txt'
}


def is_ignored(name, full_path, gitignore_patterns):
    if name in IGNORED_NAMES:
        return True
    if os.path.isfile(full_path):
        _, ext = os.path.splitext(name)
        if ext in IGNORED_EXTENSIONS:
            return True
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(full_path, pattern):
            return True
    return False


def generate_filetree(start_path, prefix='', gitignore_patterns=None):
    lines = []
    try:
        entries = sorted(os.listdir(start_path))
    except (PermissionError, FileNotFoundError):
        return [f"{prefix}└── [Error] {start_path}"]

    for i, entry in enumerate(entries):
        full_path = os.path.join(start_path, entry)
        if is_ignored(entry, full_path, gitignore_patterns):
            continue

        connector = '└── ' if i == len(entries) - 1 else '├── '
        lines.append(f"{prefix}{connector}{entry}")

        if os.path.isdir(full_path) and not os.path.islink(full_path):
            extension = '    ' if i == len(entries) - 1 else '│   '
            sub_tree = generate_filetree(full_path, prefix + extension, gitignore_patterns)
            lines.extend(sub_tree)

    return lines


def write2file(output_path='../resources/filetree.txt'):
    gitignore_patterns = load_gitignore_patterns()
    tree_lines = ['/backend', *generate_filetree('../../', gitignore_patterns=gitignore_patterns)]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree_lines))
    print(f"文件树已保存到: {output_path}")


def update_readme(tree_path='../resources/filetree.txt', readme_path='../../README.md'):
    if not os.path.exists(tree_path):
        print("正在生成文件树")
        write2file(tree_path)

    with open(tree_path, 'r', encoding='utf-8') as f:
        tree_content = f.read()

    if not os.path.exists(readme_path):
        print("README 文件不存在")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split("```")

    if len(parts) < 3:
        new_content = content.strip() + "\n\n```shell\n" + tree_content + "\n```"
    else:
        parts[1] = f"shell\n{tree_content}\n"
        new_content = "```".join(parts)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


"""该文件不需要依赖于fastapi应用"""
if __name__ == '__main__':
    update_readme()
