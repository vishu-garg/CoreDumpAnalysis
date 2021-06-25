class levenshtein_distUtil:

    def __init__(self) -> None:

        pass

    def calculate_dist(self,frames1, weights1, frames2, weights2):
        matrix = [[0.0 for _ in range(len(frames1) + 1)] for _ in range(len(frames2) + 1)]

        prev_column = matrix[0]

        for i in range(len(frames1)):
            prev_column[i + 1] = prev_column[i] + weights1[i]

        if len(frames1) == 0 or len(frames2) == 0:
            return sum(weights1)+sum(weights2)

        curr_column = matrix[1]

        for i2 in range(len(frames2)):

            frame2 = frames2[i2]
            weight2 = weights2[i2]

            curr_column[0] = prev_column[0] + weight2

            for i1 in range(len(frames1)):

                frame1 = frames1[i1]
                weight1 = weights1[i1]

                if frame1 == frame2:
                    curr_column[i1 + 1] = prev_column[i1]
                else:
                    change = weight1 + weight2 + prev_column[i1]
                    remove = weight2 + prev_column[i1 + 1]
                    insert = weight1 + curr_column[i1]

                    curr_column[i1 + 1] = min(change, remove, insert)

            if i2 != len(frames2) - 1:
                prev_column = curr_column
                curr_column = matrix[i2 + 2]

        return curr_column[-1]