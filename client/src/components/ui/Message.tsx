type Props = {
    title: string;
    message: string;
}

function Message({title, message}: Props) {
    return (
        <div className="absolute text-white m-4 p-4 bg-red inset-x-0 top-0">
            <h3 className="font-bold">{title}</h3>
            <p>{message}</p>
        </div>
    );
}

export default Message;