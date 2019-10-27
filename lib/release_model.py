class ReleaseStatusSummary():
    """
    :param definition_name: Name of ReleaseDefinition.
    :type definition_name: str
    :param release_name: Name of release deployed using this ReleaseDefinition.
    :type release_name: str
    :param approval_status: Approval status.
    :type approval_status: str
    :param status: Status environment summary.
    :type status: str
    """

    _attribute_map = {
        'definition_name': {'key': 'definition_name', 'type': 'str'},
        'release_name': {'key': 'release_name', 'type': 'str'},
        'approval_status': {'key': 'approval_status', 'type': 'str'},
        'status': {'key': 'status', 'type': 'str'},
    }

    def __init__(self, definition_name=None, release_name=None, approval_status=None, status=None):
        self.definition_name = definition_name
        self.release_name = release_name
        self.approval_status = approval_status
        self.status = status