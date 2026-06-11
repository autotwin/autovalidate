from pathlib import Path
import shutil

def collect_files_by_keyword(source_dir: Path, 
                             keywords: list, 
                             extension: str | None = None) -> list:

    """
    Searches for files with specified keywords in their file name in specified path

    Args:
        source_dir : Specified Path to search for files into
        keywords : Specified keywords to look in file name
        extension (Optional) : Specified extension of file to look in file name
    
    Returns:
        A sorted list with absolute path of the file names matching
    """

    matches = []
    
    if not source_dir.exists():
        raise FileNotFoundError(f"Path does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_dir}")

    for path in source_dir.rglob('*'):
        if path.is_file() and any(k in path.name for k in keywords):
            if extension is None or path.name.endswith(extension):
                matches.append(path)

    return sorted(matches)

def copy_files(file_paths_list: list[Path], target_dir: Path):

    """
    Moves the files to the target directory

    Args:
        file_paths_list : List of all the absolute paths for files to be moved
        target_dir : Target directory where files to be moved

    """

    target_dir.mkdir(exist_ok=True, parents= True)

    for files in file_paths_list:
        shutil.copy(files, target_dir)

def create_mri_convert_command(mri_convert_path: Path, 
                               input_file: Path,
                               output_file: Path,
                               like_path: Path | None = None,
                               resample_type: str | None = None) -> list:
    
    """
    Returns a list containing the mri_convert command to be executed

    Args:
        mri_convert_path : Path to the mri_convert command
        input_file : Path to the file to be converted
        output_file : Path to the output file after conversion
        like_path (Optional) : Define a reference file
        resample_type (Optional) : Define resample type
    
    Returns:
        A list containing the command to run
    """

    if (like_path is None) != (resample_type is None):
        raise ValueError("Reference file AND Resample Type need to be defined")    
    
    if like_path is None and resample_type is None: 
        convert_cmd = [
            str(mri_convert_path),
            str(input_file),
            str(output_file),
        ]

    else:
        convert_cmd = [
            str(mri_convert_path),
            "--resample_type", resample_type,
            str(input_file),
            "--like", str(like_path),
            str(output_file),
        ]

    return convert_cmd

def create_ants_apply_transforms_command(ants_path: Path,
                                         input_image: Path,
                                         reference_image: Path, 
                                         transform_mat: Path, 
                                         output_image: Path,
                                         interpolation="NearestNeighbor") -> list:
    
    """
    Returns a list containing the ants transformation command to be executed

    Args:
        ants_path : Path to the ants command
        input_image : Path to the file to be transformed
        reference_image : Path to the reference file
        transform_mat : Path to the transformation matrix
        output_image : Path to the output file after transformation
        interpolation : Interpolation type
    
    Returns:
        A list containing the command to run
    """

    command_line = [
        str(ants_path),
        "-d", "3",
        "-i", str(input_image),
        "-r", str(reference_image),
        "-t", str(transform_mat),
        "-n", interpolation,
        "-o", str(output_image),
    ]

    return command_line