# Referencing the GASD specifications from another repository

Add the GASD repository to your project to keep the specifications available as a local reference. Both methods below put the repository contents under `GASDSpecs/`, so you can refer to a spec by path, such as `GASDSpecs/GASD-1.2/GASD_Specification.md`.

Run the commands from the root of **your project’s repository**, on the branch you want to update. Start with a clean working tree and at least one commit. Choose one method for the initial setup and start with `GASDSpecs/` absent.

## Git subtree

A subtree tracks the GASD files as part of your project, so a regular clone includes them. `--prefix=GASDSpecs` sets the destination, and `main` selects the upstream branch.

**Use `--squash` on the initial `git subtree add` and on every `git subtree pull`.** Git groups the upstream changes for each import or update into a single snapshot commit and merges that commit into your branch. See the [Git subtree manual](https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc).

### Add the subtree

```sh
git subtree add --prefix=GASDSpecs --squash \
  https://github.com/General-Agentic-Software-Design/General-Agentic-Software-Design-Language.git main
```

### Pull upstream updates

Run this when you want to bring changes from GASD’s `main` into your project. The command fetches and merges the changes in one step.

```sh
git subtree pull --prefix=GASDSpecs --squash \
  https://github.com/General-Agentic-Software-Design/General-Agentic-Software-Design-Language.git main
```

### Use a named remote (optional)

Register `GASDSpecs` as a short name for the upstream URL once per clone where you plan to use it.

```sh
git remote add GASDSpecs https://github.com/General-Agentic-Software-Design/General-Agentic-Software-Design-Language.git
```

Use the short name in the initial `add` command or in later `pull` commands. The `GASDSpecs` after `--prefix=` is the directory. The other `GASDSpecs` is the remote name.

```sh
git subtree add --prefix=GASDSpecs --squash GASDSpecs main
```

```sh
git subtree pull --prefix=GASDSpecs --squash GASDSpecs main
```

To inspect the upstream tip before merging, run `git fetch GASDSpecs main` and then `git log -1 FETCH_HEAD`.

## Git submodule

A submodule keeps GASD as a separate Git checkout. Your project records the upstream URL in `.gitmodules` and pins `GASDSpecs/` to an exact GASD commit. See the [Git submodule manual](https://git-scm.com/docs/git-submodule).

### Add the submodule

Run `git submodule add` to stage `.gitmodules` and the initial commit reference. `-b main` selects the branch used for upstream updates.

```sh
git submodule add -b main \
  https://github.com/General-Agentic-Software-Design/General-Agentic-Software-Design-Language.git GASDSpecs
git commit -m "Add GASD specs as a submodule"
```

### Check out the recorded version

Collaborators can clone your project with `git clone --recurse-submodules`. From an existing clone, run the command below to populate `GASDSpecs/` after cloning or to check out the recorded GASD commit after pulling project changes.

```sh
git submodule update --init -- GASDSpecs
```

### Advance to a newer GASD commit

From a project clone with the submodule initialized, fetch and check out the latest commit on GASD’s `main`. Stage and commit the new reference in your project so collaborators get the same revision.

```sh
git submodule update --remote --checkout -- GASDSpecs
git add GASDSpecs
git commit -m "Update GASD specs"
```
