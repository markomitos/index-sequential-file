class Node:
    def __init__(self,value_left,left,value_right=-1,right=None):
        self.left= left
        self.right= right
        self.value_left = value_left
        self.value_right = value_right

    def __str__(self):
        return "Left value: " + str(self.value_left) + ", right value: " + str(self.value_right)

class Leaf:
    def __init__(self,block_value,block_address,overflow_value,overflow_address):
        self.block_value=block_value
        self.block_address=block_address
        self.overflow_value=overflow_value
        self.overflow_address=overflow_address

    def __str__(self):
        return "Block value: " + str(self.block_value) + ", block address: " + str(self.block_address) + ", overflow value: " + str(self.overflow_value) + ", overflow address: " + str(self.overflow_address)