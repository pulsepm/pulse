import os
import tomli
import tomli_w
import keyboard
import logging
import click
from typing import Optional, Literal
from ...core.core_dir import CONFIG_FILE, safe_open

VALID_VALUES = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]


class User:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()  # Load config on first creation
        return cls._instance


    def _load(self):
        with safe_open(CONFIG_FILE, 'rb') as u:
            if not u:
                self._create()
                return
            dt = tomli.load(u)
            self.git_user = dt["user"]
            self.git_token = dt["token"]
            self.log_power = dt["log"]
            self.stroke_dumps = dt["stroke"]
            self.just_created = False
            self.mark_for_delete = False

    def __del__(self):
        if self.mark_for_delete and os.path.isfile(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            logging.info("User configuration has been deleted successfully.")

    def _create(self):
        tx = """                Welcome dear user
       This is Pulse User configuration Wizard.
    It looks like you're here for the first time?
        This software requires usage of GitHub.
    If you don't use it, skip GitHub related steps
            Press any key to continue...
        """
        click.echo_via_pager(tx)
        keyboard.read_event(suppress=True)
        self.git_user = click.prompt("Your GitHub username", type=str)
        self.git_token = click.prompt("Your GitHub access token (https://github.com/settings/personal-access-tokens/new)", type=str)
        self.log_power = click.prompt("Your logging power (https://media.geeksforgeeks.org/wp-content/uploads/Python-log-levels.png)", type=click.Choice([str(v) for v in VALID_VALUES]), show_choices=True) # Change to pulse 
        self.stroke_dumps = click.confirm("Dump strokes? (provide_link)", default=True)
        self.log_power = max(logging.NOTSET, min(self.log_power, logging.CRITICAL))
        self.mark_for_delete = False
        self.just_created = True
        user = {
            "user": self.git_user,
            "token": self.git_token,
            "log": self.log_power,
            "stroke": self.stroke_dumps
        }
        with safe_open(CONFIG_FILE, 'wb') as u:
            tomli_w.dump(user, u)

        logging.info("You've successfully created set your Pulse profile. Now you can roll!")

    def modify_prompt(self):
        tx = """                  Welcome dear user
          This is Pulse User configuration Wizard.
      It looks like you came here to modify something?
  If so, simply press 'Enter' otherwise just press anything."""
        click.echo_via_pager(tx)
        key = keyboard.read_key(suppress=True)
        if key.lower() == "enter":
            logging.debug("Prompting the choices list...")
            self._prompt_choices()
        
    def _save(self, data):
        logging.debug(f"Saving data to {CONFIG_FILE}")
        with safe_open(CONFIG_FILE, 'wb') as f:
            tomli_w.dump(data, f)
            logging.info("Data has been saved.")

    def _prompt_choices(self):
        tx = """Please press the number on your keyboard corresponding to a listed choice.
1. GitHub username
2. GitHub Token
3. Log power
4. Stroke dumps
5. Exit with saving
6. Exit without saving"""
        click.echo_via_pager(tx)
        keyboard.read_event(suppress=True)
        option = keyboard.read_key(suppress=True)
        try:
            match int(option):
                case 1:
                    self.git_user = click.prompt(f"- The current username is: {self.git_user}.\nInput your desired GitHub username", type=str)
                case 2:
                    self.git_token = click.prompt(f"- The current access token is: {self.git_token}.\nInput your desired GitHub Access Token", type=str)
                case 3:
                    self.log_power = int(click.prompt(f"- The current logpower value is: {self.log_power}.\nInput your desired logging power value", type=click.Choice([str(v) for v in VALID_VALUES]), show_choices=True))
                case 4:
                    self.stroke_dumps = click.confirm(f"- Dumping strokes is currently: {self.stroke_dumps}.\nDump strokes?", default=self.stroke_dumps)
                case 5:
                    self._save({
                        "user": self.git_user,
                        "token": self.git_token,
                        "log": self.log_power,
                        "stroke": self.stroke_dumps
                    })
                    return
                case 6:
                    logging.debug("Exiting without saving...")
                    return

        except ValueError:
            logging.error("Invalid integer specified.")
            
        self._prompt_choices()
                