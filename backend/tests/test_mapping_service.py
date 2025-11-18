from backend.app.models.bom import BOMItem
from backend.app.models.scenario import Scenario
from backend.app.services.mapping_service import MappingService
from backend.app.data_providers.lci_provider_base import LCIProcessCandidate, LCIProvider


class _FakeProvider:
    name = "fake"

    def find_candidates(self, item: BOMItem):
        return [
            LCIProcessCandidate(
                provider=self.name,
                dataset_id="mat123",
                name="dataset",
                description="desc",
                confidence_score=0.8,
                mapping_rule_id="rule1",
                metadata={},
            )
        ]


def test_mapping_service_selects_candidate():
    item = BOMItem(
        id="i1",
        product_id="p1",
        description="Aluminum part",
        classification="123",
        material_code="AL",
        component_code=None,
        mass_kg=2.0,
        quantity=1,
    )
    scenario = Scenario(
        id="default",
        name="Default",
        goal_scope="",
        system_boundary="",
        geography="",
        method_profile_id="iso-basic",
        energy_mix_profile="",
        end_of_life_model="",
    )
    service = MappingService(providers=[_FakeProvider()])
    decisions = service.map_bom([item], scenario)
    assert decisions[0].selected is not None
    assert decisions[0].selected.dataset_id == "mat123"
