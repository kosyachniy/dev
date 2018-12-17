from func.steam import *


print(api.ISteamUser.ResolveVanityURL(vanityurl="valve", url_type=2))

client = SteamClient()
client.cli_login()

print("Logged on as: %s" % client.user.name)
print("Community profile: %s" % client.steam_id.community_url)
print("Last logon: %s" % client.user.last_logon)
print("Last logoff: %s" % client.user.last_logoff)
print("Number of friends: %d" % len(client.friends))

client.logout()