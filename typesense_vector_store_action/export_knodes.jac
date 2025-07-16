import logging;
import traceback;
import from logging { Logger }
import from jivas.agent.core.agent { Agent }
import from jivas.agent.action.action { Action }
import from jivas.agent.action.actions { Actions }
import from jivas.agent.action.agent_graph_walker { agent_graph_walker }


walker export_knodes(agent_graph_walker) {

    has as_json:bool = False;
    has with_embeddings:bool = False;
    has with_ids:bool = False;
    has response:str = "";

    # set up logger
    static has logger:Logger = logging.getLogger(__name__);

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
    }

}