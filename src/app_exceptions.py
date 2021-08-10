class LowerThanZeroBalanceException(BaseException):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return 'Balance could not be lower than zero'

    def __str__(self):
        return 'Balance could not be lower than zero'
