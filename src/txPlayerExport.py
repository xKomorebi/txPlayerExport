import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu
import json
import csv
from datetime import datetime

class PlayerDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Data Filter")

        # Initialize an empty list to store player data
        self.players_data = []

        # Initialize filter variables
        self.filter_playername = tk.StringVar()
        self.filtered_players = []

        # Set up the frame for buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        # Set up the frame for the treeview
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Add the 'Upload JSON' button
        self.upload_button = ttk.Button(button_frame, text="Upload JSON", command=self.load_json)
        self.upload_button.pack(side=tk.LEFT, padx=10)

        # Add the 'Export to CSV' button
        self.export_button = ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(side=tk.RIGHT, padx=10)

        # Add filter entry (no need for the filter button)
        self.filter_entry = ttk.Entry(button_frame, textvariable=self.filter_playername)
        self.filter_entry.pack(side=tk.LEFT, padx=10)

        # Set up the Treeview to display the data
        self.tree = ttk.Treeview(self.tree_frame, columns=('playername', 'discordID', 'lastConnectionDate'), show='headings')
        self.tree.heading('playername', text='Player Name', command=lambda: self.treeview_sort_column(self.tree, 'playername'))
        self.tree.heading('discordID', text='Discord ID', command=lambda: self.treeview_sort_column(self.tree, 'discordID'))
        self.tree.heading('lastConnectionDate', text='Last Connection Date', command=lambda: self.treeview_sort_column(self.tree, 'lastConnectionDate'))
        self.tree.column('playername', stretch=tk.YES)
        self.tree.column('discordID', stretch=tk.YES)
        self.tree.column('lastConnectionDate', stretch=tk.YES)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Create a context menu
        self.context_menu = Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_player)

        # Bind right-click event to show the context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.process_players(data.get('players', []))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while reading the file: {e}")

    def process_players(self, players):
        self.players_data = []
        for player in players:
            last_connection_date = datetime.utcfromtimestamp(player.get('tsLastConnection', 0)).strftime('%Y-%m-%d %H:%M:%S')
            discord_id = next((id_string.split(':')[1] for id_string in player.get('ids', []) if id_string.startswith('discord:')), None)
            self.players_data.append({
                'playername': player.get('displayName', 'N/A'),
                'discordID': discord_id,
                'lastConnectionDate': last_connection_date
            })
        self.filtered_players = self.players_data  # Initialize filtered_players with all data
        self.update_display()

    def update_display(self):
        # Clear the existing data in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insert new player data
        for player in self.filtered_players:
            self.tree.insert('', 'end', values=(player['playername'], player['discordID'], player['lastConnectionDate']))

    def apply_filter(self):
        filter_text = self.filter_playername.get().lower()
        self.filtered_players = [player for player in self.players_data if filter_text in player['playername'].lower()]
        self.update_display()

    def export_to_csv(self):
        if self.filtered_players:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=["playername", "discordID", "lastConnectionDate"])
                        writer.writeheader()
                        writer.writerows(self.filtered_players)
                    messagebox.showinfo("Success", "The data was successfully exported to CSV.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while writing to the file: {e}")
        else:
            messagebox.showinfo("Info", "There is no data to export.")

    def treeview_sort_column(self, tv, col):
        # Sort in ascending (A-Z) and descending (Z-A) order when clicking on column headers
        data = [(tv.set(k, col), k) for k in tv.get_children('')]
        data.sort()
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col))
        for i, item in enumerate(data):
            tv.move(item[1], '', i)

    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.context_menu.post(event.x_root, event.y_root)

    def edit_player(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_item = selected_item[0]
            player_details = self.tree.item(selected_item, 'values')
            self.show_edit_popup(player_details)

    def show_edit_popup(self, player_details):
        edit_popup = tk.Toplevel(self.root)
        edit_popup.title("Edit Player Details")

        # Create labels and entry widgets for editing
        tk.Label(edit_popup, text="Discord ID:").grid(row=0, column=0)
        discord_id_entry = tk.Entry(edit_popup)
        discord_id_entry.grid(row=0, column=1)
        discord_id_entry.insert(0, player_details[1])

        tk.Label(edit_popup, text="Player Name:").grid(row=1, column=0)
        playername_entry = tk.Entry(edit_popup)
        playername_entry.grid(row=1, column=1)
        playername_entry.insert(0, player_details[0])

        tk.Label(edit_popup, text="Last Connection Date:").grid(row=2, column=0)
        last_connection_date_entry = tk.Entry(edit_popup)
        last_connection_date_entry.grid(row=2, column=1)
        last_connection_date_entry.insert(0, player_details[2])

        # Create a save button to update player details
        save_button = ttk.Button(edit_popup, text="Save", command=lambda: self.save_player_details(player_details[0], discord_id_entry.get(), playername_entry.get(), last_connection_date_entry.get()))
        save_button.grid(row=3, column=0, columnspan=2)

    def save_player_details(self, original_playername, discord_id, playername, last_connection_date):
        # Update the player's details in self.players_data
        for player in self.players_data:
            if player['playername'] == original_playername:
                player['discordID'] = discord_id
                player['playername'] = playername
                player['lastConnectionDate'] = last_connection_date
                break

        # Update the Treeview and close the edit popup
        self.update_display()
        self.root.focus_set()  # Return focus to the main window

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerDataApp(root)
    root.mainloop()