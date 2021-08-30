import ChatPanel from "../../chat/components/ChatPanel";

const NotFoundPage = () => {
  return (
    <div className="columns p-4">
      <div className="column is-one-quarter"></div>
      <div className="column is-half">
        <div className="box has-text-centered">
          404: tech bunnies couldn't find what you're looking for :(
        </div>
      </div>
      <div className="column is-one-quarter">
        <ChatPanel></ChatPanel>
      </div>
    </div>
  );
};

export default NotFoundPage;
