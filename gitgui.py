import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from git import Repo, GitCommandError
import git
import os
from collections import defaultdict
from tkinter import ttk, filedialog, messagebox
from git import Repo
class GitGui:
    def __init__(self, master):
        self.master = master
        self.repo = None
        self.git = None
        self.auto_commit_var = tk.BooleanVar(master, value=False)
        self.auto_commit_check = tk.Checkbutton(master, text='Auto Commit', var=self.auto_commit_var, command=self.auto_commit)
        self.recover_button = tk.Button(master, text='Recover Uncommitted Changes', command=self.recover_changes)
        self.auto_commit_check = tk.Checkbutton(master, text='Auto Commit', variable=self.auto_commit_var)
        self.auto_commit_var.trace('w', self.auto_commit)
        self.recover_button = tk.Button(master, text='Recover Uncommitted Changes', command=self.recover_changes)
        self.auto_commit_check.grid(row=6, column=0)
        self.recover_button.grid(row=4, column=1)
        self.path = tk.StringVar(master, value='No path selected')
        self.commit_hash = tk.StringVar(master, value='')

        self.path_entry = tk.Entry(master, textvariable=self.path, width=50)
        self.select_button = tk.Button(master, text="Select Folder", command=self.select_folder)
        self.commit_button = tk.Button(master, text="Commit Changes", command=self.commit_changes)
        self.log_button = tk.Button(master, text='View Log', command=self.view_log)
        self.checkout_button = tk.Button(master, text='Checkout', command=self.checkout)
        self.commit_option = ttk.Combobox(master)

        self.commit_entry = tk.Entry(master, textvariable=self.commit_hash, width=50)

        self.log_text = tk.Text(master, height=20, width=100)
        self.scroll_bar = tk.Scrollbar(master)
        self.current_branch = 'master'
        self.path_entry.grid(row=0, column=0)
        self.select_button.grid(row=0, column=1)
        self.commit_button.grid(row=1, column=0)
        self.log_button.grid(row=1, column=1)
        self.log_text.grid(row=2, column=0, columnspan=3)
        self.scroll_bar.grid(row=2, column=3, sticky='ns')
        self.commit_entry.grid(row=3, column=0)
        self.checkout_button.grid(row=3, column=1)
        self.commit_option.grid(row=3, column=2)

        self.log_text.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.log_text.yview)

        self.branch_var = tk.StringVar(master)
        self.branch_dropdown = ttk.Combobox(master, textvariable=self.branch_var)
        self.branch_dropdown.grid(row=4, column=0)
        self.branch_dropdown.bind("<<ComboboxSelected>>", self.select_branch)

        # Add merge functionality
        self.merge_source_var = tk.StringVar(master)
        self.merge_target_var = tk.StringVar(master)
        self.merge_source_dropdown = ttk.Combobox(master, textvariable=self.merge_source_var)
        self.merge_target_dropdown = ttk.Combobox(master, textvariable=self.merge_target_var)
        self.merge_button = tk.Button(master, text='Merge branches', command=self.merge)
        self.merge_source_dropdown.grid(row=5, column=0)
        self.merge_target_dropdown.grid(row=5, column=1)
        self.merge_button.grid(row=5, column=2)
    def select_folder(self):

        folder = filedialog.askdirectory()
        self.path.set(folder)

        try:
            if not os.path.exists(os.path.join(folder, '.git')):
                self.repo = Repo.init(folder)
                self.git = self.repo.git
                if len(os.listdir(folder)) != 0:  # if the directory is not empty
                    try:
                        # Initial commit
                        self.git.add('--all')
                        self.git.commit('-m', 'Initial commit')
                    except GitCommandError:
                        # In case there is nothing to commit
                        pass
                self.current_branch = self.repo.active_branch.name
            else:
                self.repo = Repo(folder)
                self.git = self.repo.git
                self.current_branch = self.repo.active_branch.name
            self.update_commit_option()
        except InvalidGitRepositoryError as e:
            messagebox.showinfo('Error', f'Invalid git repository: {folder}')
    
    def commit_changes(self, auto=False):
        self.git.add('-A')

        try:
            if not self.repo.is_dirty():  # check if there are any changes in the repo
                if not auto:
                    messagebox.showinfo('Info', 'No changes to commit')
                return
            self.git.add('-A')
            self.git.commit('-m', 'commit changes')

            # logic to create a new branch if we are committing from a previous commit (not head)
            selected_commit = self.commit_option.get()
            head_commit = str(self.repo.head.commit)

            if selected_commit and selected_commit != head_commit:
                branch_name = f'From_{selected_commit[:8]}'
                while branch_name in self.repo.branches:
                    branch_name += 'x'
                self.git.branch(branch_name, selected_commit)
                self.git.checkout(branch_name)

            if not auto:
                messagebox.showinfo('Info', 'Changes committed')
            self.update_commit_option()

        except GitCommandError as e:
            messagebox.showinfo('Error', f'Error committing changes: {str(e)}')


    def view_log(self):
        self.log_text.delete('1.0', tk.END)
        try:
            log = self.git.log()
            self.log_text.insert(tk.END, log)
        except GitCommandError as e:
            messagebox.showinfo('Error', f'No logs found: {str(e)}')

    def checkout(self):
        commit = self.commit_option.get() or self.commit_hash.get()
        try:
            self.update_commit_option()
            self.git.checkout(commit)
            messagebox.showinfo('Info', f'Checkout to commit: {commit} successful')
        except GitCommandError as e:
            messagebox.showinfo('Error', f'Checkout failed: {str(e)}')
    def update_commit_option(self):

        try:
            #self.current_branch = self.repo.active_branch.name
            self.commit_option['values'] = [commit.hexsha for commit in self.repo.iter_commits(self.current_branch, max_count=None)]
        except Exception as e:
            messagebox.showinfo('Error', 'Error updating commit option: ' + str(e))
        self.commit_option['values'] = [commit.hexsha for commit in self.repo.iter_commits(self.current_branch, max_count=None)]
        #self.auto_commit_var = tk.BooleanVar(self.master, value=False)
        self.auto_commit_check = tk.Checkbutton(self.master, text='Auto Commit', var=self.auto_commit_var, command=self.auto_commit)
        self.recover_button = tk.Button(self.master, text='Recover Uncommitted Changes', command=self.recover_changes)

        self.auto_commit_check.grid(row=6, column=0)
        self.recover_button.grid(row=4, column=1)
        self.branches = [str(branch) for branch in self.repo.branches]
        self.branch_var.set(self.branches[0])
        self.branch_dropdown['values'] = self.branches
        self.merge_source_var.set(self.branches[0])
        self.merge_target_var.set(self.branches[0])
        self.merge_source_dropdown['values'] = self.branches
        self.merge_target_dropdown['values'] = self.branches
    def auto_commit(self, *args):
        if self.auto_commit_var.get():
            self.commit_changes(auto=True)  # commit changes if any exists
            self.master.after(120000, self.auto_commit)

    def recover_changes(self):
        try:
            self.git.stash('apply')
            messagebox.showinfo('Info', 'Recovered uncommitted changes')
        except GitCommandError as e:
            messagebox.showinfo('Error', f'Recovering changes failed: {str(e)}')
    def select_branch(self, event):
        self.git.checkout(self.branch_var.get())
        self.update_commit_option()

    def merge(self):
        source_branch = self.merge_source_var.get()
        target_branch = self.merge_target_var.get()
        try:
            self.git.checkout(target_branch)
            self.git.merge(source_branch)
            self.update_commit_option()
            messagebox.showinfo('Success', f'Merge of {source_branch} to {target_branch} successful')
        except Exception as e:
            messagebox.showinfo('Error', f'Merge failed: {str(e)}')
if __name__ == "__main__":
    root = tk.Tk()
    git_gui = GitGui(root)
    root.mainloop()
