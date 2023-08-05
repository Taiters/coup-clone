import styles from "./GameLog.module.css";

type MessageData<T extends MessageDataType> = {
    type: T,
    data: MessageDataTypeMap[T],
}

type MessageDataTypeMap = {
    'name': NameMessageData,
    'text': TextMessageData,
    'action': ActionMessageData,
}

type MessageDataType = keyof MessageDataTypeMap;

type NameMessageData = {
    name: string,
    color: string,
}

type TextMessageData = string;

type ActionMessageData = {
    name: string,
    color: string,
}

type Message = MessageData<MessageDataType>[];

const Name = ({ name, color }: { name: string, color: string }) =>
    <b style={{ color }}>{name}</b>;

const Action = ({ name, color }: { name: string, color: string }) =>
    <b style={{ color, fontStyle: "italic" }}>{name}</b>;

const messages: Message[] = [
    [
        {
            type: "name",
            data: {
                name: "Danny boy",
                color: "red",
            }
        },
        {
            type: "text",
            data: "opened a can of",
        },
        {
            type: "action",
            data: {
                name: "whoop ass",
                color: "blue",
            },
        },
        {
            type: "text",
            data: "on",
        },
        {
            type: "name",
            data: {
                name: "Hank Schrader",
                color: "green",
            },
        }
    ],
    [
        {
            type: "name",
            data: {
                name: "Steve Gomez",
                color: "purple",
            }
        },
        {
            type: "text",
            data: "took",
        },
        {
            type: "action",
            data: {
                name: "income",
                color: "orange",
            },
        },
    ]
]

function renderMessageData(messageData: MessageData<MessageDataType>) {
    switch (messageData.type) {
        case 'name':
            return <Name {...messageData.data as NameMessageData} />
        case 'action':
            return <Action {...messageData.data as ActionMessageData} />
        case 'text':
            return messageData.data as TextMessageData;
    }
}

function GameLog() {
    const renderedMessages = messages.map((message, i) => (
        <p className={styles.message} key={i}>
            {message.flatMap((part, j) => {
                if (j > 0) {
                    return [' ', renderMessageData(part)];
                }
                return renderMessageData(part);
            })}
        </p>
    ));
    return (
        <div className={styles.container}>
            <p>Welcome to yet another Coup clone!</p>
            {renderedMessages}
        </div>
    )
}

export default GameLog;