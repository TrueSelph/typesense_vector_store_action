import from jivas.agent.core.agent { Agent }
import from jivas.agent.action.action { Action }
import from jivas.agent.action.actions { Actions }
import from jivas.agent.action.agent_graph_walker { agent_graph_walker }


walker add_texts(agent_graph_walker) {

    has texts:list = [];
    has metadatas:list = [];
    has response:list = [];

    can on_agent with Agent entry {
        visit [-->](`?Actions);
    }

    can on_actions with Actions entry {
        visit [-->](`?Action)(?enabled==True)(?label=='TypesenseVectorStoreAction');
    }

    can on_action with Action entry {

        self.response = here.add_texts(
            texts = self.texts,
            metadatas = self.metadatas
        );

    }

}