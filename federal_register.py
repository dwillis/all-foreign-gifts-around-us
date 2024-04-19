import json
import requests

class FederalRegisterAPI:
    base_url = "https://www.federalregister.gov/api/v1/documents"

    def get_documents(self, term, agencies=None, page=1):
        params = {
            "conditions[term]": term,
            "format": "json",
            "page": page,
        }

        if agencies:
            params["conditions[agencies][]"] = agencies

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    api = FederalRegisterAPI()
    response = api.get_documents('"Gifts to Federal Employees from Foreign Government Sources"', agencies=["state-department"])
    with open("federal_register.json", "w") as outfile:
        json.dump(response, outfile)