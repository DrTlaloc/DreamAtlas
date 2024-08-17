from DreamAtlas import *

PATH = r'C:\Users\amyau\PycharmProjects\mapTlaloc\DreamAtlas\examples\\'
summer_smackdowns = ['smackdown_ea1', 'smackdown_ea2', 'smackdown_ma', 'smackdown_la']

index = 1
zegma = summer_smackdowns[index]

# Load settings
settings = DreamAtlasSettings(index+1)
settings.read_settings_file(filename=PATH+zegma+'.dream')

smackdown_map = DreamAtlasGenerator(settings=settings)

# Make the files
smackdown_map.map_title = [None, zegma, zegma+'_plane2']
smackdown_map.publish(location=PATH, name=zegma)

# Plot map images
smackdown_map.layout.plot()
smackdown_map.plot()
plt.show()
