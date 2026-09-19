# Circular Compartment Train (CCT-Set) Implementation
import math

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class Compartment:
    def __init__(self, low, high, start_node=None):
        self.low = low
        self.high = high
        self.start_node = start_node
        self.size = 0
        self.bitmap = set()  # Simulation of the O(1) bit-mask filter for duplicates

    def contains_range(self, val):
        return self.low <= val <= self.high

class CircularCompartmentTrain:
    def __init__(self, min_val=0, max_val=100):
        self.total_elements = 0
        # Start with a single compartment spanning the initial range
        initial_comp = Compartment(min_val, max_val)
        self.compartments = [initial_comp]
        self.head = None

    def _get_max_allowed_size(self):
        n = self.total_elements
        if n == 0:
            return 10
        return math.ceil(math.sqrt(n) + (0.05 * n))

    def insert(self, val):
        # 1. Look from the center (Check the indexing compartments)
        comp = None
        for c in self.compartments:
            if c.contains_range(val):
                comp = c
                break
        
        if not comp:
            # Out of bounds fallback: extend the last compartment's range
            comp = self.compartments[-1]
            comp.high = max(comp.high, val)

        # 2. O(1) Duplicate Prevention Layer (Bitmap Simulation)
        if val in comp.bitmap:
            return False  # Instantly rejected without traversing the train cars

        # 3. Insertion into the doubly linked list within this compartment
        new_node = Node(val)
        comp.bitmap.add(val)
        comp.size += 1
        self.total_elements += 1

        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            comp.start_node = new_node
        else:
            if comp.start_node is None:
                # Find nearest prior node or attach to head
                curr = self.head
                while curr.data < val and curr.next != self.head:
                    curr = curr.next
                comp.start_node = new_node
                # Insert before curr
                prev_node = curr.prev
                prev_node.next = new_node
                new_node.prev = prev_node
                new_node.next = curr
                curr.prev = new_node
            else:
                # Walk locally within the compartment to maintain order
                curr = comp.start_node
                inserted = False
                # Local traversal within compartment limits
                for _ in range(comp.size + 1):
                    if curr.data >= val:
                        prev_node = curr.prev
                        prev_node.next = new_node
                        new_node.prev = prev_node
                        new_node.next = curr
                        curr.prev = new_node
                        if curr == comp.start_node:
                            comp.start_node = new_node
                        inserted = True
                        break
                    if curr.next == self.head or curr.next.data > comp.high:
                        break
                    curr = curr.next
                
                if not inserted:
                    # Append at the local boundary of the compartment
                    next_node = curr.next
                    curr.next = new_node
                    new_node.prev = curr
                    new_node.next = next_node
                    next_node.prev = new_node

        # Update global head if needed
        if val < self.head.data:
            self.head = new_node

        # 4. Check balancing threshold and trigger split if necessary
        if comp.size > self._get_max_allowed_size():
            self._split_compartment(comp)

        return True

    def _split_compartment(self, comp):
        # Calculate new midpoint threshold for ranges
        mid_val = (comp.low + comp.high) // 2
        
        # Create a new sibling compartment
        new_comp = Compartment(mid_val + 1, comp.high)
        comp.high = mid_val

        # Redistribute bitmap filter values
        old_bitmap = comp.bitmap
        comp.bitmap = {v for v in old_bitmap if v <= mid_val}
        new_comp.bitmap = {v for v in old_bitmap if v > mid_val}

        # Recalculate sizes
        comp.size = len(comp.bitmap)
        new_comp.size = len(new_bitmap) if 'new_bitmap' in locals() else len(new_comp.bitmap)

        # Re-index the starting wagon for the new compartment
        curr = comp.start_node
        new_start = None
        for _ in range(comp.size + new_comp.size + 2):
            if curr.data > mid_val:
                new_start = curr
                break
            curr = curr.next
            if curr == self.head:
                break
        
        new_comp.start_node = new_start

        # Insert new slice into the center index list
        idx = self.compartments.index(comp)
        self.compartments.insert(idx + 1, new_comp)

    def display(self):
        if not self.head:
            return "Empty Train"
        elements = []
        curr = self.head
        while True:
            elements.append(str(curr.data))
            curr = curr.next
            if curr == self.head:
                break
        return " -> ".join(elements) + " -> (Back to Start)"

# Quick verification test
if __name__ == "__main__":
    train = CircularCompartmentTrain(0, 100)
    for num in [25, 10, 45, 22, 25, 80, 12, 23]:
        added = train.insert(num)
        print(f"Insert {num:2d}: {'Success' if added else 'Rejected (Duplicate)'}")
    
    print("
Final Indexed Compartments (Pie Slices):")
    for i, c in enumerate(train.compartments):
        print(f"  Compartment {i+1} [Range {c.low:3d}-{c.high:3d}]: Size={c.size}")
    
    print("
Logical Train Structure:")
    print(train.display())
