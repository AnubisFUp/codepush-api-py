import requests
import sys

"""
Все методы можно найти здесь
https://openapi.appcenter.ms/
"""

class Codepush:

    def __init__(self, token):
        self.token = token
        self.url = "https://api.appcenter.ms/v0.1/"
        self.headers = {"Accespt": "application/json", "X-API-Token": self.token}

    def orgs(self):
        """Возвращает список объектов организации для аккаунта кодепуша.
        """
        r = requests.get(self.url + "orgs", headers=self.headers)
        orgs = []
        for org in r.json():
            orgs.append(self.Org(self, org['name']))
        return orgs

    def isOrg(self, aoid):
        """Возвращает объект организации если она есть в аккаунте.
        Проверяет наличие искомой организации в орг-ях аккаунта
        В качестве названия ор-ии используется ее abstractorganization_id (MAIN_AOID)
        """
        orgs = self.orgs()
        for org in orgs:
            if org.name == aoid:
                print("Org --> %s is exists" %aoid)
                return org
        print('Org %s dosnt exists' %aoid)
        return False

    def createOrg(self, aoid):
        """ Создает орг-ию в аппцентре и возвращает ее объект.
        В качестве отображаемого имени и реального, рекомендуется указывать abstractorganization_id (MAIN_AOID)
        Пример орг-ии https://appcenter.ms/orgs/1868071302/manage/settings
        """
        print('Create Org %s' %aoid)
        data = {
          "display_name": aoid,
          "name": aoid
        }
        r = requests.post(self.url + "orgs", headers=self.headers, json=data)
        return self.Org(self, r.json()['name'])

    class Org:

        def __init__(self, codepush, name):
            self.name = name
            self.codepush = codepush

        def apps(self):
            """Возвращает список объектов приложений для организации.
            """
            r = requests.get(self.codepush.url + "orgs/%s/apps" % self.name, headers=self.codepush.headers)
            apps = []
            for app in r.json():
                apps.append(self.App(
                    self,
                    app['name'],
                    app['display_name'],
                    app['os'],
                    app['platform'],
                ))
            return apps

        def isApp(self, a):
            """Возарвщает объект приложения если приложение находится в списке приложений организации.
            """
            apps = self.apps()
            for app in apps:
                if app.display_name == a['display_name'] and app.os == a['os'] and app.platform == a['platform']:
                    return app
            print('App %s dosnt exists' %a['name'])                
            return False

        def createApp(self, app):
            """Создает приложение в аппцентре для организации и возвращает объект приложения.
            name - имя указываемое при релизе обновлений кодепуш (appcenter codepush release-react --app org/${name})
                уникальное для каждого приложения в организации
            display_name - имя отображаемое в админке
                может быть несколько приложений у орг-ии с одинаковым display_name именем
            os - android , ios
            platform - Objective-C / Swift, React Native, Xamarin, Unity
            """
            data = {
              "display_name": app['display_name'],
              "name": app['name'],
              "os": app['os'],
              "platform": app['platform'],
            }
            try:
                r = requests.post(self.codepush.url + "orgs/%s/apps" % self.name, headers=self.codepush.headers, json=data)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
            #print(r.json())
            app = r.json()
            return self.App(
                    self,
                    app['name'], 
                    app['display_name'], 
                    app['os'], 
                    app['platform'],
                   )

        class App:

            def __init__(self, org, name, display_name, os, platform):
                self.codepush = org.codepush
                self.org = org
                self.name = name
                self.display_name = display_name
                self.os = os
                self.platform = platform

            def deployments(self):
                """Возвращает список объектов деплойментов(окружений: prod, dev, qa) для приложения.
                """
                r = requests.get(self.codepush.url + "apps/%s/%s/deployments" % (self.org.name, self.name), headers=self.codepush.headers)
                deployments = []
                for dep in r.json():
                    deployments.append(self.Deployment(
                        self,
                        dep['name'],
                    ))
                return deployments

            def createDep(self, name):
                """Создает деплоймент в аппцентре для приложения и возвращает его объект.
                https://openapi.appcenter.ms/#/codepush/codePushDeployments_create
                """
                data = {
                  "name": name,
                }
                r = requests.post(self.codepush.url + "apps/%s/%s/deployments" % (self.org.name, self.name), headers=self.codepush.headers, json=data)
                return self.Deployment(
                        self,
                        r.json()['name'],
                    )

            def isDep(self, name):
                """Возарвщает объект деплоймента для приложения если таковой у него есть.
                """
                deps = self.deployments()
                for dep in deps:
                    if dep.name == name:
                        return dep
                print("No %s deployment for %s app" %(name, self.name))
                return False

            class Deployment:

                def __init__(self, app, name):
                    self.codepush = app.codepush
                    self.app = app
                    self.name = name

                def get(self):
                    """Возвращает json объект кодепуш деплоймента для приложения.
                    https://openapi.appcenter.ms/#/codepush/codePushDeployments_get
                    """
                    r = requests.get(self.codepush.url + "apps/%s/%s/deployments/%s" % (self.app.org.name, self.app.name, self.name), headers=self.codepush.headers)
                    return r.json()
