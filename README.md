# Gamertag

Gamertag is a bulk Xbox Live Gamertag availability checking utility.

![img](https://i.imgur.com/ajEfo09.png)

## Requirements

[Python 3.7](https://www.python.org/downloads/release/python-370/)

- [Requests](http://docs.python-requests.org/en/master/)
- [Colorama](https://pypi.org/project/colorama/)

An Xbox Live `reservationId` and `authorization` token are required. These can be acquired by sniffing network requests in the [Xbox App for Windows 10](https://www.microsoft.com/store/apps/xbox/9wzdncrfjbd8).

## Usage

Open `credentials_example.json` in your preferred text editor, input your `reservationId` and `authorization` token in the designated fields. Then rename `credentials_example.json` to `credentials.json`.

Create a text file named `list.txt`, place any desired gamertag on its own line.

```
python availability.py
```

### Output

- `available.txt` - List of gamertags available for purchase
