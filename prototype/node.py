class NodeIdentity:
    def __init__(self, node_id, address):
        """
        Initialize a new NodeIdentity with a node ID and address.
        
        :param node_id: Unique identifier for the node.
        :param address: Address of the node.
        """
        self.node_id = node_id
        self.address = address

    def __repr__(self):
        return f"NodeIdentity(node_id={self.node_id}, address={self.address})"

    def __eq__(self, other):
        if not isinstance(other, NodeIdentity):
            return False
        return self.node_id == other.node_id and self.address == other.address

    def __hash__(self):
        return hash((self.node_id, self.address))
