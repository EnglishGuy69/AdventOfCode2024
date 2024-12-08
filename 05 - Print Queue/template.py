import copy

class PrintQueue:
    def __init__(self, filename: str):
        self.page_ordering_rules = []
        self.required_pages = []
        self._load_data(filename)

    def _load_data(self, filename: str):
        with open(filename, 'r') as f:
            load_stage = 'PAGE_ORDERING_RULES'
            for row in f:
                if row.strip() == '' and load_stage == 'PAGE_ORDERING_RULES':
                    load_stage = 'PAGES_REQUIRED'
                    continue

                if load_stage == 'PAGE_ORDERING_RULES':
                    self.page_ordering_rules.append([int(x) for x in row.strip().split('|')])
                elif load_stage == 'PAGES_REQUIRED':
                    self.required_pages.append([int(x) for x in row.strip().split(',')])

    def _validate_required_pages(self, required_pages: [int]) -> bool:
        '''
        Validates that the pages to be printed are ordered according to the rules. Any rule related to pages
        not in the list to be printed are ignored.

        :param required_pages: the list of pages to be printed
        :return: True if the pages are ordered according to the rules
        '''
        error_found = False
        for rule in self.page_ordering_rules:
            (page_lower, page_higher) = rule
            if page_lower in required_pages and page_higher in required_pages:
                (index_lower, index_higher) = (required_pages.index(page_lower), required_pages.index(page_higher))
                if index_lower > index_higher:
                    error_found = True
                    break

        return not error_found

    def get_correct_order_total(self) -> int:
        '''
        Determines which sets of pages to be printed are ordered according to the rules, and then num the
        middle element of all sets that are correctly ordered.

        :return: The sum of the middle element of all pages that are ordered correctly based on the rules
        '''
        correct_order_total = 0

        for required_pages in self.required_pages:
            if self._validate_required_pages(required_pages):
                correct_order_total += required_pages[len(required_pages) // 2]

        return correct_order_total

    def correct_some_incorrect_pages(self, required_pages: [int]) -> [int]:
        '''
        Moves pages to be printed that are not in the correct position according to the rules. Note, that multiple
        passes may be required to completely correct all pages out of position.

        :param required_pages: A set of pages required to be printed
        :return: The list of pages to be printed, with some (but potentially not all) pages moved to correct positions
        '''
        required_pages = copy.copy(required_pages)
        for rule in self.page_ordering_rules:
            (page_lower, page_higher) = rule
            if page_lower in required_pages and page_higher in required_pages:
                (index_lower, index_higher) = (required_pages.index(page_lower), required_pages.index(page_higher))
                if index_lower > index_higher:
                    required_pages.pop(index_lower)
                    required_pages.insert(index_higher, page_lower)
                    pass
        return required_pages

    def get_corrected_order_total(self) -> int:
        '''
        Identifies any lists of pages that do not conform to all rules, corrects them, and then sums the mid-element
        of any sets that were corrected.

        :return: The sum of the mid-element of all incorrect page lists
        '''
        corrected_order_count = 0

        for required_pages in self.required_pages:
            if not self._validate_required_pages(required_pages):
                keep_going = True

                while keep_going:
                    new_pages = self.correct_some_incorrect_pages(required_pages)
                    keep_going = (required_pages != new_pages)
                    required_pages = new_pages

                corrected_order_count += required_pages[len(required_pages) // 2]

        return corrected_order_count

    def get_answer_1(self) -> int:
        return self.get_correct_order_total()

    def get_answer_2(self) -> int:
        return self.get_corrected_order_total()

test_solution = PrintQueue('test.txt')
assert test_solution.get_answer_1() == 143
assert test_solution.get_answer_2() == 123

solution_1 = PrintQueue('data.txt')
answer_1 = solution_1.get_answer_1()
print(f'Task 1 Answer: {answer_1}')

solution_2 = PrintQueue('data.txt')
answer_2 = solution_2.get_answer_2()
print(f'Task 2 Answer: {answer_2}')