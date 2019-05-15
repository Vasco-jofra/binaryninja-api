#include "binaryninjaapi.h"

using namespace BinaryNinja;
using namespace std;

#define RETURN_STRING(s) do { \
	char* contents = (char*)(s); \
	string result(contents); \
	BNFreeString(contents); \
	return result; \
}while(0)

RepoPlugin::RepoPlugin(BNRepoPlugin* plugin)
{
	m_object = plugin;
}

string RepoPlugin::GetPath() const
{
	RETURN_STRING(BNPluginGetPath(m_object));
}

bool RepoPlugin::IsInstalled() const
{
	return BNPluginIsInstalled(m_object);
}

void RepoPlugin::SetEnabled(bool enabled)
{
	return BNPluginSetEnabled(m_object, enabled);
}

bool RepoPlugin::IsEnabled() const
{
	return BNPluginIsEnabled(m_object);
}

PluginUpdateStatus RepoPlugin::GetPluginUpdateStatus() const
{
	return BNPluginGetPluginUpdateStatus(m_object);
}

vector<string> RepoPlugin::GetApis() const
{
	vector<string> result;
	size_t count = 0;
	char** apis = BNPluginGetApis(m_object, &count);
	result.reserve(count);
	for (size_t i = 0; i < count; i++)
		result.push_back(apis[i]);

	BNFreeStringList(apis, count);
	return result;
}

string RepoPlugin::GetAuthor() const
{
	RETURN_STRING(BNPluginGetAuthor(m_object));
}

string RepoPlugin::GetDescription() const
{
	RETURN_STRING(BNPluginGetDescription(m_object));
}

string RepoPlugin::GetLicense() const
{
	RETURN_STRING(BNPluginGetLicense(m_object));
}

string RepoPlugin::GetLicenseText() const
{
	RETURN_STRING(BNPluginGetLicenseText(m_object));
}

string RepoPlugin::GetLongdescription() const
{
	RETURN_STRING(BNPluginGetLongdescription(m_object));
}

uint64_t RepoPlugin::GetMinimimVersion() const
{
	return BNPluginGetMinimimVersion(m_object);
}

string RepoPlugin::GetName() const
{
	RETURN_STRING(BNPluginGetName(m_object));
}

vector<PluginType> RepoPlugin::GetPluginTypes() const
{
	size_t count;
	BNPluginType* pluginTypesPtr = BNPluginGetPluginTypes(m_object, &count);
	vector<PluginType> pluginTypes;
	for (size_t i = 0; i < count; i++)
	{
		pluginTypes.push_back((PluginType)pluginTypesPtr[i]);
	}
	BNFreePluginTypes(pluginTypesPtr);
	return pluginTypes;
}


string RepoPlugin::GetProjectUrl() const
{
	RETURN_STRING(BNPluginGetProjectUrl(m_object));
}


string RepoPlugin::GetPackageUrl() const
{
	RETURN_STRING(BNPluginGetPackageUrl(m_object));
}


string RepoPlugin::GetAuthorUrl() const
{
	RETURN_STRING(BNPluginGetAuthorUrl(m_object));
}


string RepoPlugin::GetVersion() const
{
	RETURN_STRING(BNPluginGetVersion(m_object));
}


string RepoPlugin::GetCommit() const
{
	RETURN_STRING(BNPluginGetCommit(m_object));
}


string RepoPlugin::GetRepository() const
{
	RETURN_STRING(BNPluginGetRepository(m_object));
}


vector<string> RepoPlugin::GetInstallPlatforms() const
{
	vector<string> result;
	size_t count = 0;
	char** platforms = BNPluginGetPlatforms(m_object, &count);
	for (size_t i = 0; i < count; i++)
		result.push_back(platforms[i]);
	BNFreeStringList(platforms, count);
	return result;
}


std::string RepoPlugin::GetInstallInstructions(const std::string& platform) const
{
	RETURN_STRING(BNPluginGetInstallInstructions(m_object, platform.c_str()));
}


bool RepoPlugin::IsBeingDeleted() const
{
	return BNPluginIsBeingDeleted(m_object);
}

bool RepoPlugin::IsBeingUpdated() const
{
	return BNPluginIsBeingUpdated(m_object);
}


string RepoPlugin::GetReadme()
{
	RETURN_STRING(BNPluginGetReadme(m_object));
}

bool RepoPlugin::Uninstall()
{
	return BNPluginUninstall(m_object);
}


bool RepoPlugin::Install()
{
	return BNPluginInstall(m_object);
}


bool RepoPlugin::Enable(bool force)
{
	return BNPluginEnable(m_object, force);
}


bool RepoPlugin::Disable()
{
	return BNPluginDisable(m_object);
}


Repository::Repository(BNRepository* r)
{
	m_object = r;
}

string Repository::GetUrl() const
{
	RETURN_STRING(BNRepositoryGetUrl(m_object));
}


string Repository::GetRepoPath() const
{
	RETURN_STRING(BNRepositoryGetRepoPath(m_object));
}


vector<Ref<RepoPlugin>> Repository::GetPlugins() const
{
	vector<Ref<RepoPlugin>> plugins;
	size_t count = 0;
	BNRepoPlugin** pluginsPtr = BNRepositoryGetPlugins(m_object, &count);
	for (size_t i = 0; i < count; i++)
		plugins.push_back(new RepoPlugin(BNNewPluginReference(pluginsPtr[i])));
	BNFreeRepositoryPluginList(pluginsPtr);
	return plugins;
}

bool Repository::IsInitialized() const
{
	return BNRepositoryIsInitialized(m_object);
}

Ref<RepoPlugin> Repository::GetPluginByPath(const string& pluginPath)
{
	return new RepoPlugin(BNNewPluginReference(BNRepositoryGetPluginByPath(m_object, pluginPath.c_str())));
}

string Repository::GetFullPath() const
{
	RETURN_STRING(BNRepositoryGetPluginsPath(m_object));
}

RepositoryManager::RepositoryManager(const string& enabledPluginsPath)
{
	m_object = BNCreateRepositoryManager(enabledPluginsPath.c_str());
}

RepositoryManager::RepositoryManager(BNRepositoryManager* mgr)
{
	m_object = mgr;
}

RepositoryManager::RepositoryManager()
{
	m_object = BNGetRepositoryManager();
}

bool RepositoryManager::CheckForUpdates()
{
	return BNRepositoryManagerCheckForUpdates(m_object);
}

vector<Ref<Repository>> RepositoryManager::GetRepositories()
{
	vector<Ref<Repository>> repos;
	size_t count = 0;
	BNRepository** reposPtr = BNRepositoryManagerGetRepositories(m_object, &count);
	for (size_t i = 0; i < count; i++)
		repos.push_back(new Repository(BNNewRepositoryReference(reposPtr[i])));
	BNFreeRepositoryManagerRepositoriesList(reposPtr);
	return repos;
}

bool RepositoryManager::AddRepository(const std::string& url,
	const std::string& repoPath) // Relative path within the repositories directory
{
	return BNRepositoryManagerAddRepository(m_object, url.c_str(), repoPath.c_str());
}

Ref<Repository> RepositoryManager::GetRepositoryByPath(const std::string& repoPath)
{
	return new Repository(BNNewRepositoryReference(BNRepositoryGetRepositoryByPath(m_object, repoPath.c_str())));
}

Ref<Repository> RepositoryManager::GetDefaultRepository()
{
	return new Repository(BNNewRepositoryReference(BNRepositoryManagerGetDefaultRepository(m_object)));
}
