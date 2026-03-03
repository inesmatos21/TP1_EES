import System.Environment (getArgs)

ackermann :: Int -> Int -> Int
ackermann 0 n = n + 1
ackermann m 0 = ackermann (m - 1) 1
ackermann m n = ackermann (m - 1) (ackermann m (n - 1))

main :: IO ()
main = do
    args <- getArgs
    let m = read (args !! 0)
    let n = read (args !! 1)
    print(ackermann m n)