from pydantic import BaseModel, Field
import yaml
import textwrap
import json


class Resource(BaseModel):
    location: str = Field(default=None, title="file or http location")
    headers: dict[str, str] | None = Field(default={}, title="List of headers, if needed, for http(s) requests")
    login: str | None = Field(default=None, title="user")
    password: str | None = Field(default=None, title="pasword")


class AuthorizationService(BaseModel):
    token_url: Resource = Field(default=None, title="Token URL of the authentication service")
    login: str = Field(default=None, title="login")
    password: str = Field(default=None, title="password")
    client_id: str | None = Field(default=None, title="Client ID")
    client_secret: str | None = Field(default=None, title="Client secret")
    grant_type: str | None = Field(default=None, title="Grant type (e.g. password)")
    arlas_iam: bool | None = Field(default=True, title="Is it an ARLAS IAM service?")


class ARLAS(BaseModel):
    persistence: Resource | None = Field(title="ARLAS Persistence Server", default=None)
    server: Resource = Field(title="ARLAS Server")
    authorization: AuthorizationService | None = Field(default=None, title="Keycloak URL")
    elastic: Resource | None = Field(default=None, title="dictionary of name/es resources")
    allow_delete: bool | None = Field(default=False, title="Is delete command allowed for this configuration?")


class Settings(BaseModel):
    arlas: dict[str, ARLAS] = Field(default=None, title="dictionary of name/arlas configurations")
    mappings: dict[str, Resource] = Field(default=None, title="dictionary of name/mapping resources")
    models: dict[str, Resource] = Field(default=None, title="dictionary of name/model resources")


class Configuration:
    settings: Settings = None

    @staticmethod
    def save(configuration_file: str):
        with open(configuration_file, 'w') as file:
            yaml.dump(Configuration.settings.model_dump(), file)

    @staticmethod
    def init(configuration_file: str) -> Settings:
        with open(configuration_file, 'r') as file:
            data = yaml.safe_load(file)
            Configuration.settings = Settings.parse_obj(data)


def __short_titles(o):
    if type(o) is dict:
        d = {}
        for key in o:
            if key == "title" and isinstance(o[key], str):
                d[key] = textwrap.shorten(o[key], 220)
            else:
                d[key] = __short_titles(o[key])                   
        return d
    if type(o) is list:
        return list(map(lambda elt: __short_titles(elt), o))
    else:
        return o


if __name__ == '__main__':
    model = __short_titles(Settings.model_json_schema())
    model["$id"] = "airs_model"
    print(json.dumps(model))
