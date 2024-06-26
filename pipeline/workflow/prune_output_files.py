import os
import shutil

import click
import luigi
from luigi.cmdline_parser import CmdlineParser
from luigi.task import flatten


# following https://luigi.readthedocs.io/en/stable/_modules/luigi/tools/deps_tree.html
def walk_tree(task, target_task):
    task_name = task.__class__.__name__

    outputs = [o.path for o in luigi.task.flatten_output(task)]

    if task_name == target_task:
        return outputs

    children = flatten(task.requires())

    ret = []
    for c in children:
        files = walk_tree(c, target_task)
        # only propagate up output targets if the target task was encountered
        if files:
            ret.extend(files)

    if ret:
        ret.extend(outputs)
    return ret


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('luigi-module-file')
@click.argument('last-task')
@click.argument('first-task')
@click.argument('luigi-args', nargs=-1)
@click.option('--dry-run', is_flag=True, default=False,
              help="dry run, don't delete files.")
def main(luigi_module_file, last_task, first_task, dry_run, luigi_args):
    """
    Determines which files are generated by tasks on a "path" of a luigi task graph and deletes them.
    This is useful to force-run one or several tasks as if the output targets already
    exist, luigi will not execute the task.

    For example if there are 4 tasks A -> B -> C -> D ('->' meaning 'requires')
    and the code of task C changed, one might to rerun tasks C, B and A. Hence,
    the output files generated by these three tasks should get deleted first.

    :param luigi_module_file: python module name containing luigi tasks (needs to be on python path)
    :param last_task: last task in topological ordering ('A' in example)
    :param first_task: first task in topological ordering ('C' in example)
    :param dry_run: don't delete files, just output paths
    :param luigi_args: arguments passed to luigi
    """

    luigi_cmd = ['--module', luigi_module_file, last_task]

    if luigi_args:
        luigi_cmd.extend(luigi_args)

    with CmdlineParser.global_instance(luigi_cmd) as cp:
        task = cp.get_task_obj()

        print("Determining output files on path {} to {}".format(first_task, last_task))
        files = walk_tree(task, first_task)

        files_to_delete = {f for f in files if os.path.exists(f)}

        if not files_to_delete:
            print("Nothing to delete.")

        for f in files_to_delete:
            if not dry_run:
                print("Removing {}".format(f))

                if os.path.exists(f):
                    if os.path.isdir(f):
                        shutil.rmtree(f)
                    else:
                        os.unlink(f)
            else:
                print("Would remove {}".format(f))


if __name__ == '__main__':
    main()
