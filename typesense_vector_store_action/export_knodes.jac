import from jivas.agent.core.agent { Agent }
import from jivas.agent.action.action { Action }
import from jivas.agent.action.actions { Actions }
import from jivas.agent.modules.action.path { action_walker_path }
import from jivas.agent.action.agent_graph_walker { agent_graph_walker }


walker export_knodes(agent_graph_walker) {

    has as_json:bool = False;
    has with_embeddings:bool = False;
    has with_ids:bool = False;
    has response:str = "";
    has reporting:bool = True;

    class __specs__ {
        static has private: bool = False;
        static has path: str = action_walker_path(__module__);
    }

    can on_agent with Agent entry {
        visit [-->](`?Actions);
    }

    can on_actions with Actions entry {
        visit [-->](`?Action)(?enabled==True)(?label=='TypesenseVectorStoreAction');
    }

    can on_action with Action entry {
        self.response = here.export_knodes(
            as_json=self.as_json,
            with_embeddings=self.with_embeddings,
            with_ids=self.with_ids
        );
        if self.reporting {
            report self.response;
        }
    }

}